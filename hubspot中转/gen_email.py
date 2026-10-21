import traceback
import json
import re
from html import escape
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

import logging

logger = logging.getLogger(__name__)


def cut_params(params):
    if 'propertiesWithHistory' in params.keys():
        params.pop('propertiesWithHistory')
    else:
        pass
    return params


def gen_email(params, max_workers=50):
    """
    批量生成email
    Args:
        params: [{}, {}, ...]
        max_workers:  [{}, {}, ...]

    Returns:

    """
    gen_email_interface = 'http://10.1.21.56:5022/gen_email'
    # gen_email_interface = 'http://localhost:5022/gen_email'
    headers = {"Content-Type": "application/json"}

    def process_single(x):
        try:
            response = requests.post(gen_email_interface, headers=headers, data=json.dumps(x)).json()

            if response.get('code', 0) == 1:
                email_body = response['model_response'].get('email_body', None)
                res = {
                    'id': x['id'],
                    'email_send': 'Ready',
                    'email_subject': response['model_response'].get('email_subject', None),
                    'email_body': email_body,
                }
                rich_email_type = (x.get('properties', {}).get('last_behavioral_email_type')
                                   or 'viewed_product_abandonment')
                # 四类邮件均双写纯文本和 HubSpot 富文本属性。
                if rich_email_type in ('viewed_promotion_abandonment', 'viewed_product_abandonment',
                                       'started_design_abandonment', 'upload_artwork_abandonment'):
                    if not isinstance(email_body, str) or not email_body.strip():
                        logger.error(f'富文本邮件正文为空，禁止回写 Ready: 用户id: {x["id"]}')
                        return {'id': x['id'], 'email_send': 'Pending',
                                'email_subject': '', 'email_body': ''}
                    # 富文本统一控制颜色、字体、行高和段落间距，避免 HubSpot 默认浅灰色和过大的空行。
                    body_for_html = email_body.strip()
                    if rich_email_type != 'viewed_promotion_abandonment':
                        # 单个换行也作为分段；署名内部保持紧凑。
                        lines = [line.strip() for line in body_for_html.splitlines()
                                 if line.strip()]
                        if rich_email_type in ('started_design_abandonment',
                                               'upload_artwork_abandonment'):
                            # 这两类生成器输出纯文本，不允许文本中的 HTML 被当成标签执行。
                            lines = [escape(line) for line in lines]
                        if (len(lines) >= 3 and lines[-3].lower() in
                                ('best regards,', 'kind regards,', 'warm regards,')
                                and lines[-1] == 'Customer Success Manager'):
                            lines[-3:] = ['<br>'.join(lines[-3:])]
                        rich_body = '<br><br>'.join(lines)
                    else:
                        rich_body = re.sub(r'\r?\n[ \t]*\r?\n', '</p><p>', body_for_html)
                        rich_body = re.sub(r'\r?\n[ \t]*', '<br>', rich_body)
                    res['email_body_rich'] = (
                        '<div style="color:#222222;font-family:Arial,sans-serif;font-size:16px;line-height:1.45;">'
                        f'<p style="margin:0 0 12px;">{rich_body}</p>'
                        '</div>'
                    )
                    # email_body_rich 为空时禁止标记 Ready，避免工作流清空旧值后留下空邮件。
                    if not res.get('email_body_rich', '').strip():
                        logger.error(f'email_body_rich 为空，禁止回写 Ready: 用户id: {x["id"]}')
                        return {
                            'id': x['id'],
                            'email_send': 'Pending',
                            'email_subject': '',
                            'email_body': '',
                        }
                logger.info(f'邮件生成完成: {x["id"]}')
                return res
            else:
                logger.warning(f'邮件生成失败: 用户id: {x["id"]}; 失败原因: {response["info"]}')
                return {
                    'id': x['id'],
                    'email_send': 'Pending',
                    'email_subject': '',
                    'email_body': ''
                }

        except Exception as e:
            logger.error(traceback.format_exc())
            return {
                'id': x['id'],
                'email_send': 'Pending',
                'email_subject': '',
                'email_body': ''
            }

    res = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_single, cut_params(x)) for x in params]
        for future in as_completed(futures):
            res.append(future.result())

    return res

if __name__ == '__main__':
    import json
    fp = '/Users/yangchengcheng/Documents/workspace/api_online/独立站相关/hubspot中转/data/contact_1.json'
    # 打开并读取json文件
    with open(fp, "r", encoding="utf-8") as f:
        data = json.load(f)  # 传入文件对象，返回dict/list
        print(data)
    res = gen_email([data])
    print(res)
