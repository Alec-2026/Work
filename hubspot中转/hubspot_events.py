"""Query HubSpot event occurrences for a contact email or ID."""

from __future__ import annotations

import os
import re
from datetime import datetime, timedelta, timezone
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


def get_contact_events(
    email: str | int | None = None,
    recent_days: int | None = None,
    max_events: int | None = None,
    access_token: str | None = None,
    timeout: int = 3600,
    *,
    record_id: str | int | None = None,
) -> dict[str, Any]:
    """Return events linked to a contact email or ID in the recent time window.

    Args:
        email: Contact email, or a positive integer/digit string contact ID.
        recent_days: Positive number of calendar days to look back from now.
        max_events: Optional maximum number of most recent events to return.
        access_token: Optional private-app token. When omitted, the function
            reads ``HUBSPOT_ACCESS_TOKEN`` and then the local ``conf.ini``.
        timeout: Timeout in seconds for each HubSpot API request.
        record_id: Explicit contact record ID, mutually exclusive with email.

    Returns:
        A dictionary containing the query window and every event occurrence.
    """

    if (email is None) == (record_id is None):
        raise ValueError("Provide exactly one of email or record_id")
    value = record_id if record_id is not None else email
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise ValueError("Contact must be an email address or a positive contact ID")
    normalized_value = str(value).strip()
    is_id = record_id is not None or isinstance(value, int) or bool(
        re.fullmatch(r"[0-9]+", normalized_value)
    )
    if is_id:
        if not re.fullmatch(r"[0-9]+", normalized_value) or not normalized_value.strip("0"):
            raise ValueError("record_id must be a positive integer or digit string")
        filter_key = "objectId"
        query_key = "query_record_id"
    else:
        normalized_value = normalized_value.lower()
        if "@" not in normalized_value or normalized_value.startswith("@"):
            raise ValueError("email must be a valid email address")
        filter_key = "objectProperty.email"
        query_key = "query_email"
    if not isinstance(recent_days, int) or isinstance(recent_days, bool) or recent_days <= 0:
        raise ValueError("recent_days must be a positive integer")
    if max_events is not None and (
        not isinstance(max_events, int)
        or isinstance(max_events, bool)
        or max_events <= 0
    ):
        raise ValueError("max_events must be a positive integer or None")
    if not isinstance(timeout, int) or isinstance(timeout, bool) or timeout <= 0:
        raise ValueError("timeout must be a positive integer")

    token = access_token or os.getenv("HUBSPOT_ACCESS_TOKEN") or _read_config_token()
    if not token or not token.strip():
        raise HubSpotAuthenticationError(
            "Provide access_token, set HUBSPOT_ACCESS_TOKEN, or configure conf.ini"
        )

    fetched_at = datetime.now(timezone.utc)
    occurred_after = fetched_at - timedelta(days=recent_days)
    client = _HubSpotClient(token.strip(), timeout)
    events: list[dict[str, Any]] = []
    after: str | None = None

    while True:
        params: dict[str, Any] = {
            "objectType": "contact",
            filter_key: normalized_value,
            "occurredAfter": occurred_after.isoformat(),
            "occurredBefore": fetched_at.isoformat(),
            "limit": 100,
        }
        if after is not None:
            params["after"] = after

        payload = client.request(
            "GET", "/events/event-occurrences/2026-03", params=params
        )
        events.extend(
            event for event in payload.get("results", []) if isinstance(event, dict)
        )
        next_after = ((payload.get("paging") or {}).get("next") or {}).get("after")
        if next_after is None:
            break
        next_after = str(next_after)
        if next_after == after:
            raise HubSpotRequestError("HubSpot returned a repeated events paging cursor")
        after = next_after

    events.sort(key=lambda event: str(event.get("occurredAt", "")), reverse=True)
    total_event_count = len(events)
    if max_events is not None:
        events = events[:max_events]
    return {
        "success": True,
        query_key: normalized_value,
        "recent_days": recent_days,
        "max_events": max_events,
        "occurred_after": occurred_after.isoformat(),
        "occurred_before": fetched_at.isoformat(),
        "event_count": len(events),
        "total_event_count": total_event_count,
        "events": events,
        "fetched_at": fetched_at.isoformat(),
    }


__all__ = [
    "get_contact_events",
    "HubSpotError",
    "HubSpotAuthenticationError",
    "HubSpotPermissionError",
    "HubSpotRequestError",
]
