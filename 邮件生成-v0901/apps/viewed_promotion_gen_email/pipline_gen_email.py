import re

from apps.viewed_promotion_gen_email import auto_tag_first
from apps.viewed_promotion_gen_email import check_email


EVENT_TYPE = 'pe243770723_viewed_promotion'


def _get_viewed_promotion_event(params):
    for event in params.get('recently_events', []):
        if event.get('eventType') == EVENT_TYPE:
            return event
    raise ValueError(f'缺失 viewed_promotion 事件: {EVENT_TYPE}')


def _clean_url(value):
    if not value:
        return ''
    return str(value).split('?', 1)[0]


def reset_params(params):
    params = dict(params)
    params['recently_events'] = [_get_viewed_promotion_event(params)]
    return params


def _valid_promotion_html(email_body, promotion_url):
    """用确定性规则校验 Promotion HTML 链接，避免 QC 模型误判 href 中的 URL。"""
    if not promotion_url:
        return '<a' not in email_body.lower()

    if (len(re.findall(r'<a\b', email_body, flags=re.IGNORECASE)) != 1
            or len(re.findall(r'</a>', email_body, flags=re.IGNORECASE)) != 1):
        return False
    links = re.findall(r'<a\s+href="([^"]+)">([^<>]+)</a>', email_body, flags=re.IGNORECASE)
    if len(links) != 1 or links[0][0] != promotion_url:
        return False
    if '?' in links[0][0] or re.search(r'\[[^\]]+\]\(https?://', email_body):
        return False

    # 去掉合法链接标签后，只检查客户可见文字中是否还残留 URL。
    visible_body = re.sub(r'<a\s+href="[^"]+">[^<>]+</a>', '', email_body, flags=re.IGNORECASE)
    return not re.search(r'https?://', visible_body, flags=re.IGNORECASE)


def pipline_first(params):
    max_retries = 3
    gen_res = {}
    event = params['recently_events'][0]
    event_properties = event.get('properties', {})
    contact_properties = params['properties']
    promotion_url = _clean_url(event_properties.get('hs_page_url', ''))
    page_slug = event_properties.get('page_name', '')

    gen_params = {
        'first_name': contact_properties.get('firstname'),
        'last_name': contact_properties.get('lastname'),
        'sender_name': contact_properties.get('dedicated_account_manager_label_for_ai_email'),
        'last_viewed_promotion_page_slug': page_slug,
        'promotion_url': promotion_url,
        'loyalty_tier': contact_properties.get('loyalty_tier', ''),
    }

    for attempt in range(max_retries):
        gen_res = auto_tag_first.AutoTag().auto_tag(gen_params)
        if gen_res.get('code') != 1 or not gen_res.get('model_response'):
            return gen_res

        check_params = {
            'first_name': gen_params['first_name'],
            'last_name': gen_params['last_name'],
            'sender_name': gen_params['sender_name'],
            'last_viewed_promotion_page_slug': page_slug,
            'promotion_url': promotion_url,
            'loyalty_tier': gen_params['loyalty_tier'],
            'email_subject': gen_res['model_response']['email_subject'],
            'email_body': gen_res['model_response']['email_body'],
        }
        check_res = check_email.AutoTag().auto_tag(check_params)
        quality_checks = (check_res.get('model_response') or {}).get('质检项目', {})
        if quality_checks:
            # URL 结构由代码确定性校验，不让模型误把合法 href 中的 URL 判为违规。
            quality_checks['URL规则'] = (
                '是' if _valid_promotion_html(gen_res['model_response']['email_body'], promotion_url) else '否'
            )
        all_passed = bool(quality_checks) and all(value == '是' for value in quality_checks.values())

        if all_passed:
            return gen_res

        if attempt == max_retries - 1:
            gen_res['code'] = 0
            gen_res['info'] = f'校验失败, 校验结果: {quality_checks}'
            return gen_res

    return gen_res


def pipline_route(params):
    """Generate the single supported first-round promotion email."""
    params = reset_params(params)
    script_round = params['properties'].get('n1v1_email_round')
    if script_round in ('round_1', None):
        return pipline_first(params)
    raise Exception('viewed_promotion 仅支持 round_1')
