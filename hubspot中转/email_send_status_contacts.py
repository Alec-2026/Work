"""Find HubSpot contacts with a non-blank email send status."""

from __future__ import annotations

import os
from typing import Any

try:
    from .hubspot_contact import (
        HubSpotAuthenticationError,
        HubSpotError,
        HubSpotPermissionError,
        HubSpotRequestError,
        _HubSpotClient,
        _read_config_token,
    )
except ImportError:  # Support importing this file directly from its directory.
    from hubspot_contact import (  # type: ignore
        HubSpotAuthenticationError,
        HubSpotError,
        HubSpotPermissionError,
        HubSpotRequestError,
        _HubSpotClient,
        _read_config_token,
    )


SEARCH_PROPERTIES = ("email", "email_send", "email_subject", "email_body")


def _is_blank(value: Any) -> bool:
    """Return whether a HubSpot property has no meaningful text value."""

    return value is None or (isinstance(value, str) and not value.strip())


def _has_email_send_status(contact: dict[str, Any]) -> bool:
    properties = contact.get("properties")
    if not isinstance(properties, dict):
        return False
    return not _is_blank(properties.get("email_send"))


def get_contacts_email_send_status(
    access_token: str | None = None,
    timeout: int = 30,
    *,
    include_history: bool = False,
) -> list[dict[str, Any]]:
    """Return complete HubSpot contacts with a non-blank email send status.

    A contact qualifies when ``email_send`` is present and non-blank. The
    function is read-only and follows every HubSpot search result page.
    Property histories are omitted unless ``include_history`` is True.
    """

    if not isinstance(timeout, int) or isinstance(timeout, bool) or timeout <= 0:
        raise ValueError("timeout must be a positive integer")

    token = access_token or os.getenv("HUBSPOT_ACCESS_TOKEN") or _read_config_token()
    if not token or not token.strip():
        raise HubSpotAuthenticationError(
            "Provide access_token, set HUBSPOT_ACCESS_TOKEN, or configure conf.ini"
        )

    client = _HubSpotClient(token.strip(), timeout)
    contact_ids: list[str] = []
    seen_ids: set[str] = set()
    after: str | None = None

    while True:
        body: dict[str, Any] = {
            "filterGroups": [
                {
                    "filters": [
                        {
                            "propertyName": "email_send",
                            "operator": "HAS_PROPERTY",
                        }
                    ]
                }
            ],
            "properties": list(SEARCH_PROPERTIES),
            "limit": 100,
        }
        if after is not None:
            body["after"] = after

        payload = client.request(
            "POST", "/crm/v3/objects/contacts/search", json=body
        )
        for contact in payload.get("results", []):
            if not isinstance(contact, dict) or not _has_email_send_status(contact):
                continue
            contact_id = contact.get("id")
            if contact_id is None:
                continue
            normalized_id = str(contact_id)
            if normalized_id not in seen_ids:
                seen_ids.add(normalized_id)
                contact_ids.append(normalized_id)

        next_after = client._next_after(payload)
        if next_after is None:
            break
        if next_after == after:
            raise HubSpotRequestError(
                "HubSpot returned a repeated contacts paging cursor"
            )
        after = next_after

    if not contact_ids:
        return []

    property_names = client.all_property_names("contacts")
    contacts = client.batch_read_objects(
        "contacts", contact_ids, property_names, include_history=include_history
    )
    contacts_by_id = {
        str(contact["id"]): contact
        for contact in contacts
        if isinstance(contact, dict) and contact.get("id") is not None
    }

    # Preserve search order and re-check the full records in case a contact was
    # edited between the search and batch-read requests.
    return [
        contacts_by_id[contact_id]
        for contact_id in contact_ids
        if contact_id in contacts_by_id and _has_email_send_status(contacts_by_id[contact_id])
    ]


__all__ = [
    "get_contacts_email_send_status",
    "HubSpotError",
    "HubSpotAuthenticationError",
    "HubSpotPermissionError",
    "HubSpotRequestError",
]
