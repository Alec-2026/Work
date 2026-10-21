from time import perf_counter

from need_email_contact import get_contacts_needing_email
from gen_email import gen_email
from upload_data import upload_contact_emails
from save_to_db import save_to_db
import uuid
import time
from hubspot_owners import get_owner_labels
from hubspot_events import get_contact_events
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import logging
from utils.logging_config import configure_logging
configure_logging()
logger = logging.getLogger(__name__)


def set_more_params(contact_params_list):
    # 获取ower对应的label
    dedicated_account_manager_list = [
        x['properties']['dedicated_account_manager']
        for x in contact_params_list
    ]

    # 获取对应的客服
    manager_id_label_map = get_owner_labels(dedicated_account_manager_list)
    for x in contact_params_list:
        x['properties']['dedicated_account_manager_label_for_ai_email'] = manager_id_label_map[x['properties']['dedicated_account_manager']]
        logger.info(
            f'获取联系人的署名中: '
            f'联系人: {x["id"]}, '
            f'联系人的署名获取完成, label: {x["properties"]["dedicated_account_manager"]}, '
            f'署名: {x["properties"]["dedicated_account_manager_label_for_ai_email"]}'
        )

    # 获取事件
    def fetch_contact_events(contact_params):
        """获取单个联系人的事件"""
        id = contact_params['id']
        result = get_contact_events(
            record_id=id,
            recent_days=7,
            max_events=100
        )
        contact_params['recently_events'] = result.get('events', [])
        return contact_params

    # 使用线程池并发处理
    max_workers = 10
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_contact_events, contact): contact for contact in contact_params_list}

        for future in tqdm(as_completed(futures), total=len(futures), desc="获取联系人事件"):
            try:
                future.result()
            except Exception as e:
                contact = futures[future]
                logger.error(f"获取联系人 {contact.get('id')} 事件时出错: {e}")

    return contact_params_list



"""
主程序
"""

def run_email_generation(max_workers: int = 50) -> dict:
    """Generate and upload emails for all eligible HubSpot contacts.

    Workflow:
    1. Read contacts whose email content has not been generated.
    2. Generate an email subject and body for every contact.
    3. Upload the generated content to the same HubSpot contact IDs.

    Returns a summary of the run. If no contacts qualify, neither the email
    generation service nor the HubSpot update endpoint is called.
    """
    random_id = str(uuid.uuid4())
    if not isinstance(max_workers, int) or isinstance(max_workers, bool) or max_workers <= 0:
        raise ValueError("max_workers must be a positive integer")

    started_at = perf_counter()
    logger.info("邮件生成任务开始：max_workers=%d", max_workers)
    logger.info("开始从 HubSpot 查询待生成邮件的联系人")
    start_time = time.time()
    contacts = get_contacts_needing_email()[:200]
    contacts_ids = [x['id'] for x in contacts]
    contacts = set_more_params(contacts)
    contact_count = len(contacts)
    attr = {
        'task_id': random_id,
        'section': '获取联系人',
        'contacts_ids': contacts_ids,
        'contact_count': contact_count,
        'use_time': time.time()-start_time
    }
    save_to_db(attr)
    start_time = time.time()

    logger.info("HubSpot 待处理联系人查询完成：contact_count=%d", contact_count)
    if not contacts:
        logger.info("没有待处理联系人，任务结束：elapsed_seconds=%.2f", perf_counter() - started_at)
        return {
            "success": True,
            "contact_count": 0,
            "generated_count": 0,
            "updated_count": 0,
            "upload_responses": [],
        }

    logger.info("开始生成邮件：contact_count=%d", contact_count)
    generated_emails = gen_email(contacts, max_workers=max_workers)
    attr = {
        'task_id': random_id,
        'section': '生成邮件',
        'contacts_ids': [x['id'] for x in generated_emails],
        'gen_mail_status': [x['email_send'] for x in generated_emails],
        'contact_count': contact_count,
        'generated_count': len(generated_emails),
        'use_time': time.time() - start_time
    }
    save_to_db(attr)
    start_time = time.time()

    if not isinstance(generated_emails, list):
        raise RuntimeError("gen_email must return a list")
    logger.info("邮件生成完成：generated_count=%d", len(generated_emails))
    if len(generated_emails) != contact_count:
        raise RuntimeError(
            "generated email count does not match the eligible contact count"
        )

    not_ready_ids = [
        str(item.get('id'))
        for item in generated_emails
        if item.get('email_send') != 'Ready'
    ]
    if not_ready_ids:
        raise RuntimeError(
            f"email generation failed; refusing HubSpot update for contacts: {not_ready_ids}"
        )

    generated_by_id = {str(item['id']): item for item in generated_emails}
    valid_uploads: list[dict] = []
    skipped_rich_ids: list[str] = []
    for item in generated_emails:
        item_id = str(item['id'])
        rich_body = generated_by_id.get(item_id, {}).get('email_body_rich')
        if item.get('email_send') == 'Ready' and (
            not isinstance(rich_body, str) or not rich_body.strip()
        ):
            skipped_rich_ids.append(item_id)
            logger.warning(
                "缺少 email_body_rich，跳过单条 HubSpot 更新: contact_id=%s",
                item_id,
            )
            continue
        valid_uploads.append(item)

    if not valid_uploads:
        logger.info("全部 Ready 邮件均缺少 email_body_rich，跳过本批次 HubSpot 回写")
        return {
            "success": True,
            "contact_count": contact_count,
            "generated_count": len(generated_emails),
            "updated_count": 0,
            "upload_responses": [],
        }

    expected_ids = {
        str(contact["id"])
        for contact in contacts
        if isinstance(contact, dict) and contact.get("id") is not None
    }
    generated_ids = {
        str(item["id"])
        for item in generated_emails
        if isinstance(item, dict) and item.get("id") is not None
    }
    if len(expected_ids) != contact_count or generated_ids != expected_ids:
        raise RuntimeError("generated emails do not match the eligible contact IDs")

    logger.info("开始回写 HubSpot：update_count=%d", len(valid_uploads))
    upload_responses = upload_contact_emails(valid_uploads)

    attr = {
        'task_id': random_id,
        'section': '上传邮件',
        'contacts_ids': contacts_ids,
        'contact_count': contact_count,
        'generated_count': len(generated_emails),
        'updated_count': len(valid_uploads),
        'use_time': time.time()-start_time,
    }
    save_to_db(attr)

    logger.info(
        "HubSpot 回写完成：updated_count=%d, batch_count=%d, skipped_rich_ids=%s",
        len(valid_uploads),
        len(upload_responses),
        skipped_rich_ids,
    )
    logger.info(
        "邮件生成任务完成：contact_count=%d, elapsed_seconds=%.2f",
        contact_count,
        perf_counter() - started_at,
    )
    return {
        "success": True,
        "contact_count": contact_count,
        "generated_count": len(generated_emails),
        "updated_count": len(valid_uploads),
        "upload_responses": upload_responses,
    }


def main() -> None:
    try:
        result = run_email_generation()
        logger.info(
            "程序执行成功：contacts=%d, generated=%d, updated=%d",
            result["contact_count"],
            result["generated_count"],
            result["updated_count"],
        )
    except Exception:
        logger.exception("程序执行失败")
        raise


if __name__ == "__main__":
    main()
