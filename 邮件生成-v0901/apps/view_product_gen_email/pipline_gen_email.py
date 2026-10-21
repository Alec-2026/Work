import html
import re
from urllib.parse import urlsplit, urlunsplit

from apps.view_product_gen_email import auto_tag_first
from apps.view_product_gen_email import auto_tag_second
from apps.view_product_gen_email import check_email

EVENT_TYPE = 'pe243770723_viewed_product'
LINK_MARKER = re.compile(r'\[\[PRODUCT_LINK\|([^\[\]\n]+)\]\]')


def _product_url(params):
    """Use only the most recent viewed_product event for the selected product."""
    product_name = str(params['properties'].get('last_viewed_product_name') or '').strip().casefold()
    if not _is_known_value(product_name):
        return ''
    events = sorted(params.get('recently_events', []),
                    key=lambda event: str(event.get('occurredAt', '')), reverse=True)
    for event in events:
        properties = event.get('properties') or {}
        if (event.get('eventType') != EVENT_TYPE
                or str(properties.get('name') or '').strip().casefold() != product_name):
            continue
        raw_url = str(properties.get('hs_page_url') or '').strip()
        try:
            parsed = urlsplit(raw_url)
            valid = (parsed.scheme.lower() == 'https'
                     and parsed.hostname == 'www.racetopprint.com'
                     and not parsed.username and not parsed.password
                     and parsed.port is None and bool(parsed.path))
        except ValueError:
            valid = False
        if not valid:
            return ''
        return urlunsplit(('https', parsed.netloc, parsed.path, '', ''))
    return ''


def _render_product_link(body, product_url, needs_link):
    if not isinstance(body, str):
        raise ValueError('商品邮件正文必须是字符串')
    markers = LINK_MARKER.findall(body)
    if needs_link and len(markers) != 1:
        raise ValueError('商品已知且页面 URL 有效时，正文必须包含一个 PRODUCT_LINK 标记')
    if not needs_link and markers:
        raise ValueError('商品链接不可用时，不得包含 PRODUCT_LINK 标记')
    without_marker = LINK_MARKER.sub('', body)
    if ('[[PRODUCT_LINK|' in without_marker or '<' in without_marker or '>' in without_marker
            or re.search(r'https?://|\[[^\]]+\]\(https?://', without_marker, re.I)):
        raise ValueError('商品邮件正文包含未受信任的链接或 HTML')
    if not needs_link:
        return body
    label = markers[0].strip()
    if not label or 'http' in label.lower() or '{' in label or '}' in label:
        raise ValueError('商品链接文字无效')
    anchor = f'<a href="{html.escape(product_url, quote=True)}">{html.escape(label)}</a>'
    return LINK_MARKER.sub(lambda _: anchor, body, count=1)


def _is_known_value(value):
    """判断联系人字段是否包含可用于模板选择的有效值。"""
    if value is None:
        return False

    normalized = str(value).strip().lower()
    return normalized not in {
        '', 'unknown', 'unknow', 'null', 'none',
        '未知', '无法判断', '未提供'
    }


def _get_template_type(product_name, industry_name):
    """按商品和行业字段是否有效，确定首轮邮件模板。"""
    product_known = _is_known_value(product_name)
    industry_known = _is_known_value(industry_name)

    if product_known and industry_known:
        return '模板A-具体商品'
    if product_known:
        return '模板B-用途导向'
    return '模板C-简短顾问型'


def pipline_first(params):
    """
    一轮话术的pipline
    Args:
        params:

    Returns:

    """
    max_retries = 3
    gen_res = {}
    page_url = _product_url(params)
    needs_link = bool(page_url and _is_known_value(params['properties']['last_viewed_product_name']))

    for attempt in range(max_retries):
        gen_params = {
            'first_name': params['properties']['firstname'],
            'last_name': params['properties']['lastname'],
            'product_name': params['properties']['last_viewed_product_name'],
            'page_url': page_url,
            'second_label': params['properties']['industry_level_2'],
            'template_type': _get_template_type(
                params['properties']['last_viewed_product_name'],
                params['properties']['industry_level_2']
            ),
            'sender_name': params['properties']['dedicated_account_manager_label_for_ai_email'],
            'discount_script': params['properties']['first_order_offer_message']
        }
        gen_res = auto_tag_first.AutoTag().auto_tag(gen_params)
        if gen_res.get('code') != 1 or not gen_res.get('model_response'):
            return gen_res
        try:
            gen_res['model_response']['email_body'] = _render_product_link(
                gen_res['model_response']['email_body'], page_url, needs_link)
        except ValueError as exc:
            if attempt == max_retries - 1:
                gen_res['code'], gen_res['info'] = 0, str(exc)
                return gen_res
            continue

        check_params = {
            'first_name': params['properties']['firstname'],
            'last_name': params['properties']['lastname'],
            'product_name': params['properties']['last_viewed_product_name'],
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
    page_url = _product_url(params)
    needs_link = bool(page_url and _is_known_value(params['properties']['last_viewed_product_name']))

    for attempt in range(max_retries):
        gen_params = {
            'first_name': params['properties']['firstname'],
            'last_name': params['properties']['lastname'],
            'product_name': params['properties']['last_viewed_product_name'],
            'page_url': page_url,
            'second_label': params['properties']['industry_level_2'],
            'sender_name': params['properties']['dedicated_account_manager_label_for_ai_email'],
            'discount_script': params['properties']['first_order_offer_message']
        }
        gen_res = auto_tag_second.AutoTag().auto_tag(gen_params)
        if gen_res.get('code') != 1 or not gen_res.get('model_response'):
            return gen_res
        try:
            gen_res['model_response']['email_body'] = _render_product_link(
                gen_res['model_response']['email_body'], page_url, needs_link)
        except ValueError as exc:
            if attempt == max_retries - 1:
                gen_res['code'], gen_res['info'] = 0, str(exc)
                return gen_res
            continue

        check_params = {
            'first_name': params['properties']['firstname'],
            'last_name': params['properties']['lastname'],
            'product_name': params['properties']['last_viewed_product_name'],
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



def pipline_route(params):
    """
    根据一轮话术和二轮话术将请求分发到first和second
    Args:
        params:

    Returns:

    """
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
            'last_viewed_product_name': 'Custom Foil Stamped Gift Bags',
            'dedicated_account_manager_label_for_ai_email': 'Megan H',
            'industry_level_2': '餐饮与美食',
            'first_order_offer_message': 'When you’re ready to place your first RacetopPrint order, you’re welcome to use code NEW20 toward the product price of the recommended product.',
            'last_behavioral_email_type': 'viewed_product_abandonment'
        }
    }

    res = pipline_route(params)
    print(res)




