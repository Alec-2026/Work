from hubspot_contact import get_contact_crm_profile
from hubspot_events import get_contact_events


"""
测试根据邮箱获取联系人信息
"""
# email = 'vicmick@gmail.com'
# profile = get_contact_crm_profile(email)
# print(profile)

"""
根据邮箱获取events
"""
# result = get_contact_events(
#     email="med240488@gmail.com",
#     recent_days=1,
#     max_events=10
# )
#
# events = result["events"]
# print(events)

"""
测试需要生成邮件的人群
"""
# from need_email_contact import get_contacts_needing_email
# import json
# import os
#
# contacts = get_contacts_needing_email()
# print(len(contacts))
#
# # Create data directory if it doesn't exist
# os.makedirs('data', exist_ok=True)
#
# # Save each contact to a JSON file
# for index, contact in enumerate(contacts):
#     filename = f'data/contact_{index + 1}.json'
#     with open(filename, 'w', encoding='utf-8') as f:
#         json.dump(contact, f, ensure_ascii=False, indent=2)
#     print(f"Saved contact {index + 1} to {filename}")


"""
测试回写功能
"""
# from upload_data import upload_contact_emails
#
#
# updates = [
#     {
#         "id": "491499076344",
#         'email_send': 'Ready',
#         "email_subject": "Your email subject",
#         "email_body": "Your email body",
#     }
# ]
#
# responses = upload_contact_emails(updates)
# print(responses)

"""
测试获取标签
"""
# from hubspot_owners import get_owner_labels
# labels = get_owner_labels(["168012531", "168012622", "168012622"])
# print(labels)


"""
测试用户状态的方法
"""
from email_send_status_contacts import get_contacts_email_send_status
res = get_contacts_email_send_status()
print(len(res))