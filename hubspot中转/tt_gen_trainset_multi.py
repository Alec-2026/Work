import pandas as pd
from tqdm import tqdm
from hubspot_contact import get_contact_crm_profile
from app import set_more_params
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
"""
生成标注的excel
"""

fp = '/Users/yangchengcheng/Documents/independent_station/hubspot中转/data/测试3-近日.xlsx'
df = pd.read_excel(fp)

def process_contact(row):
    """处理单个联系人信息"""
    id = row['记录 ID']
    profile = get_contact_crm_profile(record_id=id)
    profile = profile['contacts'][0]
    profile.pop('propertiesWithHistory')
    profile['properties'].pop('email_body')
    profile['properties'].pop('email_subject')
    return profile

# 使用线程池并发处理
profile_list = []
max_workers = 10  # 可根据需要调整并发数

with ThreadPoolExecutor(max_workers=max_workers) as executor:
    # 提交所有任务
    futures = {executor.submit(process_contact, row): index for index, row in df.iterrows()}

    # 使用tqdm显示进度
    for future in tqdm(as_completed(futures), total=len(futures), desc="获取联系人信息"):
        try:
            profile = future.result()
            profile_list.append(profile)
        except Exception as e:
            index = futures[future]
            print(f"处理第 {index} 行时出错: {e}")

profile_list = set_more_params(profile_list)


"""
以下部分是为了解析出excel
"""
# 将json保存到文件
filename = f'data/测试.json'
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(profile_list, f, ensure_ascii=False, indent=2)


email_send_list = []
last_behavioral_email_type_list = []
n1v1_email_round_list = []
firstname_list = []
lastname_list = []
sender_name_list = []
first_order_offer_message_list = []
industry_level_1_list = []
industry_level_2_list = []
product_name_list = []
spec_list = []

event_param_list = []

# 解析出需要的字段
for profile in profile_list:
    email_send = profile['properties']['email_send']
    last_behavioral_email_type = profile['properties']['last_behavioral_email_type']
    n1v1_email_round = profile['properties']['n1v1_email_round']

    firstname = profile['properties']['firstname']
    lastname = profile['properties']['lastname']
    sender_name = profile['properties']['dedicated_account_manager_label_for_ai_email']
    first_order_offer_message = profile['properties']['first_order_offer_message']
    industry_level_1 = profile['properties']['industry_level_1']
    industry_level_2 = profile['properties']['industry_level_2']

    events_list = profile['recently_events']
    event_params = {}
    flag = False
    for x in events_list:
        if x['eventType'] == 'pe243770723_started_design':
            event_params = x
            flag = True
            break


    event_param_list.append(event_params)

    product_name = event_params.get('properties', {}).get('name', '')
    spec = json.loads(event_params.get('properties', {}).get('spec', '{}'))

    product_name_list.append(product_name)
    email_send_list.append(email_send)
    last_behavioral_email_type_list.append(last_behavioral_email_type)
    n1v1_email_round_list.append(n1v1_email_round)
    firstname_list.append(firstname)
    lastname_list.append(lastname)
    sender_name_list.append(sender_name)
    first_order_offer_message_list.append(first_order_offer_message)
    industry_level_1_list.append(industry_level_1)
    industry_level_2_list.append(industry_level_2)

    spec_list.append(spec)


df['email_send'] = email_send_list
df['last_behavioral_email_type'] = last_behavioral_email_type_list
df['n1v1_email_round'] = n1v1_email_round_list
df['firstname'] = firstname_list
df['lastname'] = lastname_list
df['sender_name'] = sender_name_list
df['first_order_offer_message'] = first_order_offer_message_list
df['industry_level_1'] = industry_level_1_list
df['industry_level_2'] = industry_level_2_list
df['product_name'] = product_name_list
df['spec'] = spec_list

df['event_params'] = event_param_list


df.to_excel(fp.replace('.xlsx', '-output.xlsx'), index=False)