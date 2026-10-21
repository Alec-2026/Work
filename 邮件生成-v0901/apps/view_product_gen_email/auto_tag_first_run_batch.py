import traceback
import time
import pandas as pd
from utils.format_data import parse_str_json
from utils.utils import process_dataframe_multi_thread
from apps.view_product_gen_email import auto_tag

"""
从文件中加载测试数据
"""


def request(df):
    def process_row(row):
        response = {}
        try:
            params = row.to_dict()
            params = {
                'audio_text': params['text'],
            }
            response = auto_tag.AutoTag().auto_tag(params)['model_response']
            return response
        except Exception as e:
            traceback.print_exc()
            return response
    response_list = process_dataframe_multi_thread(df, process_row, max_workers=30)

    df['model_response'] = response_list

    return df


def parse(df):
    for x in [
        '录音总结',
        '销售环节/自我介绍/是否提及', '销售环节/客户行业/是否提及', '销售环节/使用场景/是否提及', '销售环节/推荐产品/是否提及',
        '销售环节/产品卖点/是否提及', '销售环节/案例介绍/是否提及', '销售环节/产品范围/是否提及',
        'score'
    ]:
        df[x.replace('/', '_')] = [
            parse_str_json(str(row['model_response']), x)
            for index, row in df.iterrows()
        ]

    return df


if __name__ == '__main__':
    # dataframe分块处理
    from tqdm import tqdm
    fp = 'data/语音样本-text.xlsx'
    df = pd.read_excel(fp).reset_index(drop=True)
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
