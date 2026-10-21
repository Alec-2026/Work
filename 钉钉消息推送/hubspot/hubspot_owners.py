"""根据 HubSpot 用户选项的内部名称（owner ID）获取所有者及姓名标签。

示例：get_owner_label("168012531")
认证依次使用 access_token、HUBSPOT_ACCESS_TOKEN、conf.ini 的
[hubspot] access_token。API 文档：
https://developers.hubspot.com/docs/api-reference/legacy/crm/owners/get-owner
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any

from hubspot_contact import (
    HubSpotAuthenticationError,
    HubSpotError,
    HubSpotPermissionError,
    HubSpotRequestError,
    _HubSpotClient,
    _read_config_token,
)


def _normalize_owner_id(owner_id: str | int) -> str:
    if isinstance(owner_id, bool) or not isinstance(owner_id, (str, int)):
        raise ValueError("owner_id must be a positive integer or numeric string")
    normalized_id = str(owner_id).strip()
    if not normalized_id.isascii() or not normalized_id.isdecimal() or int(normalized_id) <= 0:
        raise ValueError("owner_id must be a positive integer or numeric string")
    return str(int(normalized_id))


def get_owner(
    owner_id: str | int,
    access_token: str | None = None,
    timeout: int = 30,
    *,
    archived: bool = False,
    id_property: str = "id",
) -> dict[str, Any]:
    """返回 owner 的完整 API 数据，并添加 label 字段。

    截图中的内部名称传入 owner_id，默认按 owner 的 id 查询。
    只有传入 HubSpot userId 时才设置 id_property="userId"。
    已归档所有者需显式设置 archived=True。
    label 为 firstName + lastName；姓名为空时依次回退到邮箱、owner ID。
    无效参数抛出 ValueError；认证、权限、未找到和网络错误抛出
    对应的 HubSpotError 子类，不会将请求失败当成空标签。
    """
    normalized_id = _normalize_owner_id(owner_id)
    if id_property not in ("id", "userId"):
        raise ValueError("id_property must be 'id' or 'userId'")
    if not isinstance(archived, bool):
        raise ValueError("archived must be a boolean")
    if isinstance(timeout, bool) or not isinstance(timeout, int) or timeout <= 0:
        raise ValueError("timeout must be a positive integer")

    token = access_token or os.getenv("HUBSPOT_ACCESS_TOKEN") or _read_config_token()
    if not token or not token.strip():
        raise HubSpotAuthenticationError(
            "Provide access_token, set HUBSPOT_ACCESS_TOKEN, or configure conf.ini"
        )

    client = _HubSpotClient(token.strip(), timeout)
    try:
        owner = client.request(
            "GET",
            f"/crm/v3/owners/{normalized_id}",
            params={"idProperty": id_property, "archived": str(archived).lower()},
        )
    finally:
        client.session.close()

    if not owner.get("id"):
        raise HubSpotRequestError("HubSpot returned an owner without an id")
    name = " ".join(
        str(owner.get(field) or "").strip()
        for field in ("firstName", "lastName")
        if str(owner.get(field) or "").strip()
    )
    owner["label"] = name or str(owner.get("email") or "").strip() or str(owner["id"])
    return owner


def get_owner_label(
    owner_id: str | int,
    access_token: str | None = None,
    timeout: int = 30,
    *,
    archived: bool = False,
    id_property: str = "id",
) -> str:
    """根据内部名称获取姓名标签，例如 '168012531' 对应的姓名。"""
    return get_owner(
        owner_id, access_token, timeout, archived=archived, id_property=id_property
    )["label"]


def get_owner_labels(
    owner_ids: list[str | int],
    access_token: str | None = None,
    timeout: int = 30,
    *,
    archived: bool = False,
    id_property: str = "id",
) -> dict[str, str]:
    """批量返回 {ID字符串: 姓名标签}，按输入顺序去重后逐个查询。

    空列表返回 {}。所有 ID 在请求前校验，整数和数字字符串视为同一 ID。
    任一查询失败时抛出原有异常，不静默跳过或返回不完整的结果。
    示例：get_owner_labels(["168012531", "168012632"])
    """
    if not isinstance(owner_ids, list):
        raise ValueError("owner_ids must be a list of owner IDs")
    normalized_ids = list(dict.fromkeys(_normalize_owner_id(value) for value in owner_ids))
    return {
        owner_id: get_owner_label(
            owner_id, access_token, timeout, archived=archived, id_property=id_property
        )
        for owner_id in normalized_ids
    }


__all__ = [
    "get_owner", "get_owner_label", "get_owner_labels", "HubSpotError", "HubSpotAuthenticationError",
    "HubSpotPermissionError", "HubSpotRequestError",
]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("owner_id", help="用户选项的内部名称（owner ID）")
    parser.add_argument("--label-only", action="store_true", help="仅输出姓名标签")
    parser.add_argument("--archived", action="store_true", help="查询已归档所有者")
    parser.add_argument("--id-property", choices=("id", "userId"), default="id")
    args = parser.parse_args()
    try:
        result = get_owner(args.owner_id, archived=args.archived, id_property=args.id_property)
    except (ValueError, HubSpotError) as exc:
        parser.exit(1, f"查询失败：{exc}\n")
    print(result["label"] if args.label_only else json.dumps(result, ensure_ascii=False, indent=2))
