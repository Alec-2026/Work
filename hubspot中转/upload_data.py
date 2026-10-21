"""Upload generated email content to existing HubSpot contacts."""

from __future__ import annotations

import os
from typing import Any, Iterable

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


def _chunks(
    values: list[dict[str, Any]], size: int
) -> Iterable[list[dict[str, Any]]]:
    for index in range(0, len(values), size):
        yield values[index : index + size]


def _validated_inputs(updates: list[dict[str, str]]) -> list[dict[str, Any]]:
    if not isinstance(updates, list):
        raise ValueError("updates must be a list")

    inputs: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for index, update in enumerate(updates):
        if not isinstance(update, dict):
            raise ValueError(f"updates[{index}] must be a dictionary")

        contact_id = update.get("id")
        if not isinstance(contact_id, str) or not contact_id.strip():
            raise ValueError(f"updates[{index}].id must be a non-empty string")
        contact_id = contact_id.strip()
        if contact_id in seen_ids:
            raise ValueError(f"duplicate contact id: {contact_id}")

        for property_name in ("email_subject", "email_body", "email_send"):
            if property_name not in update:
                raise ValueError(f"updates[{index}] must include {property_name}")
            if not isinstance(update[property_name], str):
                raise ValueError(f"updates[{index}].{property_name} must be a string")

        seen_ids.add(contact_id)
        properties = {
            "email_subject": update["email_subject"],
            "email_body": update["email_body"],
            "email_send": update["email_send"],
        }
        # 只有生成链路提供富文本正文时才更新该字段，避免其他事件误清空已有 HTML 内容。
        if "email_body_rich" in update:
            if not isinstance(update["email_body_rich"], str):
                raise ValueError(f"updates[{index}].email_body_rich must be a string")
            properties["email_body_rich"] = update["email_body_rich"]

        inputs.append({"id": contact_id, "properties": properties})
    return inputs

def upload_contact_emails(
    updates: list[dict[str, str]],
    access_token: str | None = None,
    timeout: int = 30,
) -> list[dict[str, Any]]:
    """Update generated email subjects and bodies for HubSpot contacts.

    Contacts are identified by their HubSpot record IDs. Existing values are
    overwritten, and empty strings are allowed so callers can clear a field.
    The returned list contains one unmodified HubSpot response per batch.
    """

    if not isinstance(timeout, int) or isinstance(timeout, bool) or timeout <= 0:
        raise ValueError("timeout must be a positive integer")

    inputs = _validated_inputs(updates)
    if not inputs:
        return []

    token = access_token or os.getenv("HUBSPOT_ACCESS_TOKEN") or _read_config_token()
    if not token or not token.strip():
        raise HubSpotAuthenticationError(
            "Provide access_token, set HUBSPOT_ACCESS_TOKEN, or configure conf.ini"
        )

    client = _HubSpotClient(token.strip(), timeout)
    responses: list[dict[str, Any]] = []
    for input_chunk in _chunks(inputs, 100):
        responses.append(
            client.request(
                "POST",
                "/crm/v3/objects/contacts/batch/update",
                json={"inputs": input_chunk},
            )
        )
    return responses


__all__ = [
    "upload_contact_emails",
    "HubSpotError",
    "HubSpotAuthenticationError",
    "HubSpotPermissionError",
    "HubSpotRequestError",
]
