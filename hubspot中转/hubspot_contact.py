"""Read a contact's complete CRM profile from a single HubSpot account."""

from __future__ import annotations

import os
import re
import time
from configparser import ConfigParser
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any, Callable, Iterable

import requests


API_BASE_URL = "https://api.hubapi.com"
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
ACTIVITY_OBJECTS = ("emails", "calls", "meetings", "notes", "tasks")
PROFILE_OBJECTS = ("contacts", "companies", "deals", "line_items", *ACTIVITY_OBJECTS)
CONFIG_PATH = Path(__file__).with_name("conf.ini")


class HubSpotError(Exception):
    """Base exception for this module."""


class HubSpotAuthenticationError(HubSpotError):
    """The access token is missing or invalid."""


class HubSpotPermissionError(HubSpotError):
    """The private app lacks a required HubSpot scope."""


class HubSpotRequestError(HubSpotError):
    """A HubSpot API request failed."""


def _chunks(values: list[str], size: int) -> Iterable[list[str]]:
    for index in range(0, len(values), size):
        yield values[index : index + size]


class _HubSpotClient:
    def __init__(
        self,
        access_token: str,
        timeout: int,
        session: requests.Session | None = None,
        max_retries: int = 4,
    ) -> None:
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = session or requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "User-Agent": "hubspot-contact-profile/1.0",
            }
        )

    def request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        url = f"{API_BASE_URL}{path}"
        last_error: Exception | None = None

        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.request(
                    method, url, timeout=self.timeout, **kwargs
                )
            except requests.RequestException as exc:
                last_error = exc
                if attempt == self.max_retries:
                    break
                time.sleep(min(2**attempt, 8))
                continue

            if response.status_code == 401:
                raise HubSpotAuthenticationError("HubSpot access token is invalid or expired")
            if response.status_code == 403:
                raise HubSpotPermissionError(
                    "HubSpot private app does not have permission to read this resource"
                )
            if response.status_code == 404:
                raise HubSpotRequestError("Requested HubSpot resource was not found")

            if response.status_code == 429 or 500 <= response.status_code < 600:
                if attempt == self.max_retries:
                    raise HubSpotRequestError(
                        f"HubSpot API request failed after retries (HTTP {response.status_code})"
                    )
                time.sleep(self._retry_delay(response, attempt))
                continue

            if not response.ok:
                raise HubSpotRequestError(
                    f"HubSpot API request failed (HTTP {response.status_code})"
                )

            if response.status_code == 204 or not response.content:
                return {}
            try:
                payload = response.json()
            except ValueError as exc:
                raise HubSpotRequestError("HubSpot returned an invalid JSON response") from exc
            if not isinstance(payload, dict):
                raise HubSpotRequestError("HubSpot returned an unexpected response")
            return payload

        raise HubSpotRequestError("Unable to connect to HubSpot after retries") from last_error

    @staticmethod
    def _retry_delay(response: requests.Response, attempt: int) -> float:
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            try:
                return min(max(float(retry_after), 0.0), 30.0)
            except ValueError:
                try:
                    retry_time = parsedate_to_datetime(retry_after)
                    now = datetime.now(retry_time.tzinfo or timezone.utc)
                    return min(max((retry_time - now).total_seconds(), 0.0), 30.0)
                except (TypeError, ValueError, OverflowError):
                    pass
        return min(2**attempt, 8)

    def all_property_names(self, object_type: str) -> list[str]:
        payload = self.request("GET", f"/crm/v3/properties/{object_type}")
        return sorted(
            {
                item["name"]
                for item in payload.get("results", [])
                if isinstance(item, dict) and item.get("name")
            }
        )

    def search_contacts(self, value: str, property_name: str = "email") -> list[str]:
        after: str | None = None
        contact_ids: list[str] = []
        while True:
            body: dict[str, Any] = {
                "filterGroups": [
                    {
                        "filters": [
                            {
                                "propertyName": property_name,
                                "operator": "EQ",
                                "value": value,
                            }
                        ]
                    }
                ],
                "properties": [property_name],
                "limit": 100,
            }
            if after is not None:
                body["after"] = after
            payload = self.request(
                "POST", "/crm/v3/objects/contacts/search", json=body
            )
            contact_ids.extend(
                str(item["id"])
                for item in payload.get("results", [])
                if isinstance(item, dict) and item.get("id") is not None
            )
            after = self._next_after(payload)
            if after is None:
                return list(dict.fromkeys(contact_ids))

    def batch_read_objects(
        self, object_type: str, object_ids: list[str], properties: list[str],
        *, include_history: bool = True,
    ) -> list[dict[str, Any]]:
        if not object_ids:
            return []
        results: list[dict[str, Any]] = []
        # HubSpot limits batch reads that request property histories to 50
        # inputs, even though batch reads without histories support 100.
        batch_size = 50 if include_history else 100
        for id_chunk in _chunks(list(dict.fromkeys(object_ids)), batch_size):
            body = {
                "properties": properties,
                "inputs": [{"id": object_id} for object_id in id_chunk],
            }
            if include_history:
                body["propertiesWithHistory"] = properties
            payload = self.request(
                "POST", f"/crm/v3/objects/{object_type}/batch/read", json=body
            )
            results.extend(
                item for item in payload.get("results", []) if isinstance(item, dict)
            )
        return results

    def read_associations(
        self, from_type: str, to_type: str, from_ids: list[str]
    ) -> tuple[list[str], list[dict[str, Any]]]:
        if not from_ids:
            return [], []
        target_ids: list[str] = []
        associations: list[dict[str, Any]] = []
        for id_chunk in _chunks(list(dict.fromkeys(from_ids)), 1000):
            payload = self.request(
                "POST",
                f"/crm/v4/associations/{from_type}/{to_type}/batch/read",
                json={"inputs": [{"id": object_id} for object_id in id_chunk]},
            )
            for result in payload.get("results", []):
                if not isinstance(result, dict):
                    continue
                from_id = str((result.get("from") or {}).get("id", ""))
                for target in result.get("to", []):
                    if not isinstance(target, dict):
                        continue
                    target_id = target.get("toObjectId", target.get("id"))
                    if target_id is None:
                        continue
                    target_id = str(target_id)
                    target_ids.append(target_id)
                    associations.append(
                        {
                            "from_object_type": from_type,
                            "from_object_id": from_id,
                            "to_object_type": to_type,
                            "to_object_id": target_id,
                            "association_types": target.get("associationTypes", []),
                        }
                    )
        return list(dict.fromkeys(target_ids)), associations

    def read_owners(self, owner_ids: list[str]) -> list[dict[str, Any]]:
        owners: list[dict[str, Any]] = []
        for owner_id in dict.fromkeys(owner_ids):
            try:
                owners.append(self.request("GET", f"/crm/v3/owners/{owner_id}"))
            except HubSpotRequestError:
                continue
        return owners

    @staticmethod
    def _next_after(payload: dict[str, Any]) -> str | None:
        after = ((payload.get("paging") or {}).get("next") or {}).get("after")
        return str(after) if after is not None else None


def _owner_ids(records: Iterable[dict[str, Any]]) -> list[str]:
    ids: list[str] = []
    for record in records:
        properties = record.get("properties") or {}
        for key in ("hubspot_owner_id", "hs_all_owner_ids"):
            value = properties.get(key)
            if not value:
                continue
            ids.extend(part for part in str(value).split(";") if part)
    return list(dict.fromkeys(ids))


def _empty_result(query_value: str, query_key: str = "query_email") -> dict[str, Any]:
    return {
        "success": True,
        query_key: query_value,
        "matched_contacts": 0,
        "contacts": [],
        "companies": [],
        "deals": [],
        "line_items": [],
        "owners": [],
        "activities": {name: [] for name in ACTIVITY_OBJECTS},
        "associations": [],
        "warnings": [],
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


def _read_config_token() -> str | None:
    if not CONFIG_PATH.is_file():
        return None
    parser = ConfigParser()
    try:
        parser.read(CONFIG_PATH, encoding="utf-8")
        token = parser.get("hubspot", "access_token", fallback="").strip()
    except (OSError, ValueError):
        return None
    return token or None


def get_contact_crm_profile(
    email: str | int | None = None,
    access_token: str | None = None,
    timeout: int = 30,
    *,
    record_id: str | int | None = None,
) -> dict[str, Any]:
    """Return a complete CRM profile by contact email or record ID.

    Provide exactly one of ``email`` or ``record_id``. The first positional
    argument also accepts a positive integer or digit string record ID.
    Surrounding whitespace is ignored and emails are normalized to lowercase.

    The function is read-only. It returns an empty successful profile when no
    contact matches. Missing permissions for associated object types are added
    to ``warnings`` while authentication and core contact failures are raised.
    """

    if (email is None) == (record_id is None):
        raise ValueError("Provide exactly one of email or record_id")
    value = record_id if record_id is not None else email
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise ValueError("Contact must be an email address or a positive record ID")
    normalized_value = str(value).strip()
    is_id = record_id is not None or isinstance(value, int) or bool(
        re.fullmatch(r"[0-9]+", normalized_value)
    )
    if is_id:
        if not re.fullmatch(r"[0-9]+", normalized_value) or not normalized_value.strip("0"):
            raise ValueError("record_id must be a positive integer or digit string")
        property_name = "hs_object_id"
    else:
        if not EMAIL_PATTERN.fullmatch(normalized_value):
            raise ValueError("email must be a valid email address")
        normalized_value = normalized_value.lower()
        property_name = "email"
    return _get_contact_crm_profile(
        normalized_value, property_name, access_token, timeout
    )


def _get_contact_crm_profile(
    query_value: str,
    property_name: str,
    access_token: str | None,
    timeout: int,
) -> dict[str, Any]:
    if not isinstance(timeout, int) or isinstance(timeout, bool) or timeout <= 0:
        raise ValueError("timeout must be a positive integer")

    token = access_token or os.getenv("HUBSPOT_ACCESS_TOKEN") or _read_config_token()
    if not token or not token.strip():
        raise HubSpotAuthenticationError(
            "Provide access_token, set HUBSPOT_ACCESS_TOKEN, or configure conf.ini"
        )

    client = _HubSpotClient(token.strip(), timeout)
    query_key = "query_email" if property_name == "email" else "query_record_id"
    result = _empty_result(query_value, query_key)
    contact_ids = client.search_contacts(query_value, property_name)
    result["matched_contacts"] = len(contact_ids)
    if not contact_ids:
        return result
    if property_name == "email" and len(contact_ids) > 1:
        result["warnings"].append(
            f"Multiple contacts ({len(contact_ids)}) matched the email; all were returned"
        )

    property_cache: dict[str, list[str]] = {}

    def properties_for(object_type: str, optional: bool = False) -> list[str]:
        if object_type in property_cache:
            return property_cache[object_type]
        try:
            names = client.all_property_names(object_type)
        except HubSpotPermissionError:
            if not optional:
                raise
            result["warnings"].append(
                f"Skipped {object_type}: the private app lacks read permission"
            )
            names = []
        property_cache[object_type] = names
        return names

    contact_properties = properties_for("contacts")
    result["contacts"] = client.batch_read_objects(
        "contacts", contact_ids, contact_properties
    )

    all_associations: list[dict[str, Any]] = []

    def associated_ids(
        from_type: str, to_type: str, from_ids: list[str], optional: bool = True
    ) -> list[str]:
        try:
            ids, links = client.read_associations(from_type, to_type, from_ids)
        except HubSpotPermissionError:
            if not optional:
                raise
            result["warnings"].append(
                f"Skipped {from_type} to {to_type} associations: permission denied"
            )
            return []
        all_associations.extend(links)
        return ids

    def optional_records(object_type: str, object_ids: list[str]) -> list[dict[str, Any]]:
        if not object_ids:
            return []
        properties = properties_for(object_type, optional=True)
        if not properties:
            return []
        try:
            return client.batch_read_objects(object_type, object_ids, properties)
        except HubSpotPermissionError:
            result["warnings"].append(
                f"Skipped {object_type}: the private app lacks read permission"
            )
            return []

    company_ids = associated_ids("contacts", "companies", contact_ids)
    deal_ids = associated_ids("contacts", "deals", contact_ids)
    result["companies"] = optional_records("companies", company_ids)
    result["deals"] = optional_records("deals", deal_ids)

    line_item_ids = associated_ids("deals", "line_items", deal_ids)
    result["line_items"] = optional_records("line_items", line_item_ids)

    for activity_type in ACTIVITY_OBJECTS:
        activity_ids = associated_ids("contacts", activity_type, contact_ids)
        result["activities"][activity_type] = optional_records(
            activity_type, activity_ids
        )

    owner_ids = _owner_ids(
        [
            *result["contacts"],
            *result["companies"],
            *result["deals"],
            *result["line_items"],
            *(record for records in result["activities"].values() for record in records),
        ]
    )
    if owner_ids:
        try:
            result["owners"] = client.read_owners(owner_ids)
        except HubSpotPermissionError:
            result["warnings"].append(
                "Skipped owners: the private app lacks read permission"
            )

    result["associations"] = all_associations
    return result


__all__ = [
    "get_contact_crm_profile",
    "HubSpotError",
    "HubSpotAuthenticationError",
    "HubSpotPermissionError",
    "HubSpotRequestError",
]
