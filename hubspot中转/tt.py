from hubspot_contact import get_contact_crm_profile
from hubspot_events import get_contact_events
import json

"""
测试根据邮箱获取联系人信息
"""
# email = 'supplynsip@gmail.com'
# profile = get_contact_crm_profile(email)
# print(profile)
#
# filename = f'data/{email.replace(".com", "")}.json'
# with open(filename, 'w', encoding='utf-8') as f:
#     json.dump(profile, f, ensure_ascii=False, indent=2)


"""
根据ID获取联系信息
"""
# id = '542301521626'
# profile = get_contact_crm_profile(record_id=id)
# print(profile)
#
# filename = f'data/{id}.json'
# with open(filename, 'w', encoding='utf-8') as f:
#     json.dump(profile, f, ensure_ascii=False, indent=2)


"""
根据邮箱获取events
"""

# 根据id
# id = '553738458818'
# result = get_contact_events(
#     record_id=id,
#     recent_days=2,
#     max_events=100
# )
# print(result)

# # 根据id
# email = 'supplynsip@gmail.com'
# result = get_contact_events(
#     email=email,
#     recent_days=2,
#     max_events=100
# )
# print(result)



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
from upload_data import upload_contact_emails


updates = [
    {
        "id": "542301521626",
        'email_send': 'Ready',
        "email_subject": "Your email subject",
        "email_body": "Your email body",
        "email_body_rich": """Hi Alan,<br><br>I wanted to follow up on my earlier note about premium gift bags.<br><br>These bags could, for example, be used for wellness kits or patient appreciation gifts in rehabilitation and therapy settings. I can offer suggestions on presenting your branding or a supportive message based on how you plan to use them.<br><br>Whether or not you have artwork at this stage, I'd be happy to help. You're welcome to reply with either a file for review or a brief description of your idea, and I can suggest a next step.<br><br>When you're ready to place your first RacetopPrint order, you're welcome to use code NEW20 toward the product price of the recommended product.<br><br>Thank you for your time. Please feel free to reply whenever it's convenient.<br><br>you can click this button: <a href="https://www.racetopprint.com/sale/halloween-starts-with-great-packaging">the Halloween options</a><br><br>Best regards,<br>Camille Y<br>Customer Success Manager""",
    }
]

responses = upload_contact_emails(updates)
print(responses)

"""
测试获取标签
"""
# from hubspot_owners import get_owner_labels
# labels = get_owner_labels(["168012531", "168012622", "168012622"])
# print(labels)


"""
测试用户状态的方法
"""
# from email_send_status_contacts import get_contacts_email_send_status
# res = get_contacts_email_send_status()
# print(len(res))

"""
根据ID获取调用邮件生成接口的参数
"""
# from app import set_more_params
# id = '558031221486'
# profile = get_contact_crm_profile(record_id=id)
# profile = profile['contacts'][0]
# # profile.pop('propertiesWithHistory')
# profile_gen_mail = set_more_params([profile])
#
# filename = f'data/测试接口-{id}.json'
# with open(filename, 'w', encoding='utf-8') as f:
#     json.dump(profile, f, ensure_ascii=False, indent=2)
