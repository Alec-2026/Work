from apps.started_design_gen_email import auto_tag_first
from apps.started_design_gen_email import auto_tag_second
from apps.started_design_gen_email import check_email


def get_started_design_product_name(params):
    """Return the product associated with the locked started_design workflow."""
    properties = params['properties']

    # The contact property is the primary source for the workflow's product.
    product_name = properties.get('last_started_design_name')
    if isinstance(product_name, str) and product_name.strip():
        return product_name

    # Keep the event as a fallback for older/incomplete contact records.
    for event in params.get('recently_events', []):
        if event.get('eventType') != 'pe243770723_started_design':
            continue
        product_name = event.get('properties', {}).get('name')
        if isinstance(product_name, str) and product_name.strip():
            return product_name

    raise ValueError('started_design 商品为空，停止生成邮件')


def pipline_first(params):
    """
    一轮话术的pipline
    Args:
        params:

    Returns:

    """
    max_retries = 3
    gen_res = {}

    for attempt in range(max_retries):
        product_name = get_started_design_product_name(params)
        gen_params = {
            'first_name': params['properties']['firstname'],
            'last_name': params['properties']['lastname'],
            'product_name': product_name,
            'second_label': params['properties']['industry_level_2'],
            'sender_name': params['properties']['dedicated_account_manager_label_for_ai_email'],
            'discount_script': params['properties']['first_order_offer_message'],
            'spec': params['recently_events'][0].get('properties', {}).get('spec', '')
        }
        gen_res = auto_tag_first.AutoTag().auto_tag(gen_params)

        check_params = {
            'first_name': params['properties']['firstname'],
            'last_name': params['properties']['lastname'],
            'product_name': product_name,
            'sender_name': params['properties']['dedicated_account_manager_label_for_ai_email'],
            'email_subject': gen_res['model_response']['email_subject'],
            'email_body': gen_res['model_response']['email_body'],
        }
        check_res = check_email.AutoTag().auto_tag(check_params)

        # 检查所有质检项目是否通过
        quality_checks = check_res['model_response'].get('质检项目', {})
        all_passed = all(value == '是' for value in quality_checks.values())

        if all_passed:
            return gen_res

        # 如果是最后一次尝试，仍然返回结果但附带校验信息
        if attempt == max_retries - 1:
            gen_res['code'] = 0
            gen_res['info'] = f'校验失败, 校验结果: {quality_checks}'
            return gen_res


    return gen_res



def pipline_second(params):
    """
    二轮话术的pipline
    Args:
        params:

    Returns:

    """
    max_retries = 3
    gen_res = {}

    for attempt in range(max_retries):
        product_name = get_started_design_product_name(params)
        gen_params = {
            'first_name': params['properties']['firstname'],
            'last_name': params['properties']['lastname'],
            'product_name': product_name,
            'second_label': params['properties']['industry_level_2'],
            'sender_name': params['properties']['dedicated_account_manager_label_for_ai_email'],
            'discount_script': params['properties']['first_order_offer_message'],
            'spec': params['recently_events'][0].get('properties', {}).get('spec', '')
        }
        gen_res = auto_tag_second.AutoTag().auto_tag(gen_params)

        check_params = {
            'first_name': params['properties']['firstname'],
            'last_name': params['properties']['lastname'],
            'product_name': product_name,
            'sender_name': params['properties']['dedicated_account_manager_label_for_ai_email'],
            'email_subject': gen_res['model_response']['email_subject'],
            'email_body': gen_res['model_response']['email_body'],
        }
        check_res = check_email.AutoTag().auto_tag(check_params)

        # 检查所有质检项目是否通过
        quality_checks = check_res['model_response'].get('质检项目', {})
        all_passed = all(value == '是' for value in quality_checks.values())

        if all_passed:
            return gen_res

        # 如果是最后一次尝试，仍然返回结果但附带校验信息
        if attempt == max_retries - 1:
            gen_res['code'] = 0
            gen_res['info'] = f'校验失败, 校验结果: {quality_checks}'
            return gen_res


    return gen_res

def reset_params(params):
    events_list = params['recently_events']
    event_params = {}
    for x in events_list:
        if x['eventType'] == 'pe243770723_started_design':
            event_params = x
            break
    params['recently_events'] = [event_params]

    return params

def pipline_route(params):
    """
    根据一轮话术和二轮话术将请求分发到first和second
    Args:
        params:

    Returns:

    """
    params = reset_params(params)
    script_round = params['properties']['n1v1_email_round']
    if script_round == 'round_1' or script_round is None:
        return pipline_first(params)
    elif script_round == 'round_2':
        return pipline_second(params)
    else:
        raise Exception('不支持该模型轮次, 当前支持的模型轮次有: [round_1, round2]')



if __name__ == '__main__':
    params = {
        'properties': {
            'n1v1_email_round': 'round_2',
            'firstname': 'Isa',
            'lastname': 'Fernandez',
            'dedicated_account_manager_label_for_ai_email': 'Megan H',
            'industry_level_2': '餐饮与美食',
            'first_order_offer_message': 'When you’re ready to place your first RacetopPrint order, you’re welcome to use code NEW20 toward the product price of the recommended product.',
            'last_behavioral_email_type': 'viewed_product_abandonment'
        },
        'recently_events': [{
            'objectType': 'CONTACT',
            'objectId': '553738458818',
            'eventType': 'e_visited_page',
            'occurredAt': '2026-09-22T22:50:17.331Z',
            'id': 'leviathan-4d0099bd-b697-354c-9a8b-3673202ff49c-1790117417331',
            'properties': {
                'hs_base_url': 'www.racetopprint.com/cart',
                'hs_url': 'https://www.racetopprint.com/cart',
                'hs_region': 'az',
                'hs_is_virtual_url': 'false',
                'hs_is_virtual_referrer': 'false',
                'hs_is_external': 'true',
                'hs_browser_fingerprint': '2dd3953d0882395f05c242fa0f7d1f9e',
                'hs_cf_bot_score': '37',
                'hs_hash_id': '551419',
                'hs_is_new_cookie': 'false',
                'hs_historical_contact_lifecyclestage': 'lead',
                'hs_log_line_timestamp': '1790117417331',
                'hs_browser': 'Chrome',
                'hs_country': 'us',
                'hs_canonical_url': 'www.racetopprint.com/cart',
                'hs_url_domain': 'racetopprint.com',
                'hs_url_path': '/cart',
                'hs_operating_system': 'Windows',
                'hs_processed_timestamp': '1790117418246',
                'hs_targeted_content_aggregation': 'default',
                'hs_analytics_normalized_page_url': 'https://www.racetopprint.com/cart',
                'hs_device_type': 'Desktop',
                'hs_qualified_region': 'us_az',
                'hs_visit_source': 'direct',
                'hs_page_id': 'www.racetopprint.com/cart',
                'hs_referrer': 'https://www.racetopprint.com/cart',
                'hs_user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36',
                'hs_city': 'chandler',
                'hs_is_amp': 'false',
                'hs_browser_version_major': '153',
                'hs_is_in_chat_view': 'false',
                'hs_is_contact': 'true',
                'hs_leviathan_linked_vids': '553738458818;554585017073',
                'hs_utm_campaign': '',
                'hs_visit_source_details_2': 'c90e6907-e895-479c-8689-0d22fa660677',
                'hs_browser_type': 'Browser',
                'hs_visit_source_details_1': 'www.racetopprint.com/labels-stickers'
            }
        }, {
            'objectType': 'CONTACT',
            'objectId': '553738458818',
            'eventType': 'e_workflow_unenrolled_v2',
            'occurredAt': '2026-09-22T22:50:16.169Z',
            'id': '243770723-1709795042036-workflow_unenrolled_v2',
            'properties': {
                'hs_notification_type': 'success',
                'hs_flow_id': '4828045043',
                'hs_final_state': 'completed',
                'hs_source_app': '4',
                'hs_enrollment_id': '1709795042036',
                'hs_source': '',
                'hs_unenroll_type': '',
                'hs_automation_flow': '243770723-0-44-842421161686'
            }
        }
    ]
    }

    res = pipline_route(params)
    print(res)



