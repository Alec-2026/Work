import traceback
import time
import pandas as pd
from utils.format_data import parse_str_json
from utils.utils import process_dataframe_multi_thread
from apps.viewed_promotion_gen_email.auto_tag_first import AutoTag

"""
从 Excel 文件中加载 viewed_promotion 测试数据，并批量生成 Promotion 邮件。
"""


def request(df):
    def process_row(row):
        response = {}
        try:
            row = row.to_dict()

            params = {
                'first_name': row['first_name'],
                'last_name': row['last_name'],
                'sender_name': row['sender_name'],
                'last_viewed_promotion_page_slug': row['last_viewed_promotion_page_slug'],
                'promotion_url': row['promotion_url'],
                'loyalty_tier': row['loyalty_tier'],
            }
            # 使用 viewed_promotion 专用 AutoTag，直接复用现有 Prompt 和 HTML 链接处理。
            response = AutoTag().auto_tag(params)['model_response']
            return response
        except Exception:
            traceback.print_exc()
            return response

    response_list = process_dataframe_multi_thread(df, process_row, max_workers=30)
    df['model_response'] = response_list
    return df


def parse(df):
    for field in [
        '选择的模版',
        'email_subject',
        'email_body',
        '生成依据',
    ]:
        df[field] = [
            parse_str_json(str(row['model_response']), field)
            for _, row in df.iterrows()
        ]
    return df


if __name__ == '__main__':
    from tqdm import tqdm

    # 前端 viewed_promotion 工作区使用同一份 Excel 数据源。
    fp = '/Users/alec/Documents/gitlab/email_send/viewed_promotion测试数据_v2.xlsx'
    df = pd.read_excel(fp).reset_index(drop=True)
    batch_size = 10000
    df_output = pd.DataFrame()
    start = time.time()

    for i in tqdm(
        range(0, df.shape[0], batch_size),
        total=max(df.shape[0] / batch_size, 1),
        desc='分块处理dataframe'
    ):
        tmp_df_output = request(df[i:i + batch_size].reset_index(drop=True))
        df_output = pd.concat([df_output, tmp_df_output]).reset_index(drop=True)
        df_output.to_excel(fp.replace('.xlsx', '-output.xlsx'), index=False)
        df_format = parse(df_output)
        df_format.to_excel(fp.replace('.xlsx', '-output-format.xlsx'), index=False)

    print('总花费时长: ', int(time.time() - start), 's')
