import time
import hmac
import hashlib
import base64
import datetime
import traceback
import urllib.parse
import requests
from utils import get_config


def _format_cell(value):
    """把单元格的值转成字符串，None/空串统一显示为 '-'。"""
    if value is None or value == '':
        return '-'
    if isinstance(value, (datetime.datetime, datetime.date)):
        return value.strftime('%Y-%m-%d')
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, float) and value.is_integer():
        return f'{int(value):,}'
    if isinstance(value, int):
        return f'{value:,}'
    return str(value).replace('|', '\\|').replace('\n', ' ')


# 推送指标配置：(SQL 列名, 表格表头)
_HUBSPOT_COLUMNS = [
    ('date', '日期'),
    ('任务数量', '任务数'),
    ('获取数量', '获取联系人数'),
    ('Ready数量', '成功邮件数'),
    ('Pending数量', '失败邮件数'),
    ('上传的数量', '上传邮件数'),
]


def _format_date_range(rows):
    """取首尾日期，渲染「2026-09-15 ~ 2026-09-16」这样的区间文案。"""
    dates = [_format_cell(row.get('date')) for row in rows if row.get('date')]
    if not dates:
        return ''
    first, last = dates[-1], dates[0]
    return first if first == last else f'{first} ~ {last}'


def format_hubspot_markdown(rows, title='邮件后台数据'):
    """
    把 get_hubspot_info() 返回的 [{列名: 值}, ...] 渲染成钉钉 markdown 表格。
    :param rows: 数据行列表（按日期倒序）
    :param title: 消息标题
    :return: 钉钉 markdown 文本；无数据时返回 None
    """
    if not rows:
        return None

    headers = [name for _, name in _HUBSPOT_COLUMNS]
    date_range = _format_date_range(rows)
    lines = [f'### {title}']
    if date_range:
        lines.append(f'**数据日期：{date_range}**')
    lines += [
        '> 共 {} 条 · 生成时间 {}'.format(len(rows), datetime.datetime.now().strftime('%Y-%m-%d %H:%M')),
        '',
        '| ' + ' | '.join(headers) + ' |',
        '| ' + ' | '.join(['---'] * len(headers)) + ' |',
    ]
    for row in rows:
        lines.append('| ' + ' | '.join(_format_cell(row.get(col)) for col, _ in _HUBSPOT_COLUMNS) + ' |')

    return '\n'.join(lines)



def format_hubspot_status_markdown(hubspot_status_data):
    """将按轮次汇总的邮件状态转为 Markdown；空数据返回提示文案。"""
    statuses = ['Wait', 'Ready', 'Pending', 'Review Completed', 'Sent']
    rounds = [('round_1', '第一轮'), ('round_2', '第二轮')]
    status_data = hubspot_status_data or {}
    wait_total = sum(status_data.get(key, {}).get('Wait', 0) for key, _ in rounds)
    ready_total = sum(status_data.get(key, {}).get('Ready', 0) for key, _ in rounds)
    status_lines = [
        '### 邮件线上状态',
        '**当前日期：{}**'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        f'> 待生成数量：{wait_total} · 待审核数量：{ready_total}',
        '',
    ]
    if hubspot_status_data:
        status_lines.extend([
            '| 发送轮次 | ' + ' | '.join(statuses) + ' |',
            '| ' + ' | '.join(['---'] * (len(statuses) + 1)) + ' |',
        ])
        for round_key, round_name in rounds:
            counts = hubspot_status_data.get(round_key, {})
            status_lines.append(
                '| ' + round_name + ' | '
                + ' | '.join(str(counts.get(status, 0)) for status in statuses)
                + ' |'
            )
    else:
        status_lines.append('暂无邮件发送状态数据。')

    return '\n'.join(status_lines)


def send_message_to_dingding(message, title='HubSpot 数据提醒', msgtype='markdown'):
    # 钉钉机器人配置
    # 钉钉机器人的加签名
    conf = get_config()
    secret = conf['dingding']['secret']
    access_token = conf['dingding']['access_token']

    if not message:
        print('消息内容为空，跳过推送')
        return False

    # 钉钉机器人Webhook地址
    # secret = 'SECba9e7d5f140ab7f2b419fa750b952c6269207c4e2b946a1d4ca32f0f63bb6bcb'
    # access_token = 'https://oapi.dingtalk.com/robot/send?access_token=fdfc37d73447d4af3376879ffe485bc43a5fcdd14abffd832d27b99a0ba822a7'

    # 消息推送
    try:
        timestamp = str(round(time.time() * 1000))
        secret_enc = secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        url = f"{access_token}&timestamp={timestamp}&sign={sign}"
        if msgtype == 'markdown':
            data = {
                "msgtype": "markdown",
                "markdown": {"title": title, "text": message},
            }
        else:
            data = {
                "msgtype": "text",
                "text": {"content": message},
            }
        response = requests.post(url, json=data)
        response.raise_for_status()
        print("POST 请求响应状态码:", response.status_code)
        print("POST 请求响应内容:", response.json())
        result = response.json()
        if result.get('errcode') == 0:
            return True
        print('钉钉消息推送被拒绝:', result.get('errmsg'))
        return False
    except Exception as e:
        traceback.print_exc()
        print('钉钉消息推送失败')
        return False


if __name__ == '__main__':
    send_message_to_dingding('在吗', msgtype='text')
