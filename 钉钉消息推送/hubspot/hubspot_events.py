"""Query HubSpot event occurrences for a contact email."""

from __future__ import annotations

import os
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
    email: str,
    recent_days: int,
    max_events: int | None = None,
    access_token: str | None = None,
    timeout: int = 30,
) -> dict[str, Any]:
    """Return all HubSpot events linked to an email in the recent time window.

    Args:
        email: Contact email used by HubSpot to associate event occurrences.
        recent_days: Positive number of calendar days to look back from now.
        max_events: Optional maximum number of most recent events to return.
        access_token: Optional private-app token. When omitted, the function
            reads ``HUBSPOT_ACCESS_TOKEN`` and then the local ``conf.ini``.
        timeout: Timeout in seconds for each HubSpot API request.

    Returns:
        A dictionary containing the query window and every event occurrence.
    """

    if not isinstance(email, str) or not email.strip():
        raise ValueError("email must not be empty")
    normalized_email = email.strip().lower()
    if "@" not in normalized_email or normalized_email.startswith("@"):
        raise ValueError("email must be a valid email address")
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
            "objectProperty.email": normalized_email,
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
        "query_email": normalized_email,
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
