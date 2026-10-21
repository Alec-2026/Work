import traceback
import time
import pandas as pd
from utils.format_data import parse_str_json
from utils.utils import process_dataframe_multi_thread
from apps.started_design_gen_email.auto_tag_first import AutoTag

"""
从文件中加载测试数据
"""


def request(df):
    def process_row(row):
        response = {}
        try:
            row = row.to_dict()
            params = {
                'first_name': row['first_name'],
                'product_name': row['product_name'],
                'sender_name': row['product_name'],
                'second_label': row['second_label'],
                'discount_script': row['discount_script'],
                'spec': row['spec']
            }
            response = AutoTag().auto_tag(params)['model_response']
            return response
        except Exception as e:
            traceback.print_exc()
            return response
    response_list = process_dataframe_multi_thread(df, process_row, max_workers=30)

    df['model_response'] = response_list

    return df


def parse(df):
    for x in [
        '用户信息总结',
        '选择的模版',
        'email_subject',
        'email_body',
        '生成依据',
    ]:
        df[x] = [
            parse_str_json(str(row['model_response']), x)
            for index, row in df.iterrows()
        ]

    return df


if __name__ == '__main__':
    # dataframe分块处理
    from tqdm import tqdm
    fp = '/Users/yangchengcheng/Documents/independent_station/邮件生成-v0901/apps/started_design_gen_email/data/测试数据.xlsx'
    df = pd.read_excel(fp).reset_index(drop=True)[:30]
    batch_size = 10000
    df_output = pd.DataFrame()
    start = time.time()
    for i in tqdm(range(0, df.shape[0], batch_size), total=max(df.shape[0]/batch_size,1), desc='分块处理dataframe'):
        tmp_df_output = request(df[i:i + batch_size].reset_index(drop=True))
        df_output = pd.concat([df_output, tmp_df_output]).reset_index(drop=True)
        df_output.to_excel(fp.replace('.xlsx', '-output.xlsx'), index=False)
        df_format = parse(df_output)
        df_format.to_excel(fp.replace('.xlsx', '-output-format.xlsx'), index=False)
    print('总花费时长: ', int(time.time() - start), 's')
