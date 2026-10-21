from message_dingding import (
    send_message_to_dingding,
    format_hubspot_markdown,
    format_hubspot_status_markdown,
)
from get_db_info import DataBaseLog
from get_hubspot_info import get_contacts_email_send_status


def send_message():
    hubspot_trans_data = DataBaseLog().get_hubspot_info()
    hubspot_trans_data_md = format_hubspot_markdown(hubspot_trans_data)
    hubspot_status_data = get_contacts_email_send_status()
    hubspot_status_data_md = format_hubspot_status_markdown(hubspot_status_data)

    # 空行结束 Markdown 表格，再通过显式换行标签增加两部分之间的间距。
    section_separator = '\n\n--- \n\n'
    send_message_md = section_separator.join([
        hubspot_status_data_md,
        hubspot_trans_data_md or '### HubSpot 后台数据\n\n暂无日报数据。',
    ])
    send_message_to_dingding(send_message_md)


if __name__ == '__main__':
    send_message()
