import pandas as pd
from openpyxl import load_workbook
from tqdm import tqdm
from openpyxl.drawing import image
import requests
from io import BytesIO
import traceback


# 将图片放置到Excel中
def put_image_to_excel(excel_path, image_path_feature, put_image_feature, image_type='path', top_row_number=500):
    """
    将图片放置到excel中
    参数：
    excel_path: 原始excel的地址
    image_path_feature: 图片地址所在的列
    put_image_feature: 图片需要放到的列
    image_type: 图片地址的类型：path or url
    return: None，保存到excel中，原始excel地址加_image的后缀
    """
    if top_row_number == -1:
        df = pd.read_excel(excel_path)
    else:
        df = pd.read_excel(excel_path, nrows=top_row_number)
    save_path = excel_path[:-5]+'_image'+'.xlsx'
    df.to_excel(save_path, sheet_name='sheet1', index=False)
    wb = load_workbook(save_path)
    ws = wb['sheet1']
    for index, row in tqdm(df.iterrows(), total=df.shape[0], desc='图片填充'):
        # 解析图片地址，支持地址、地址列表、换行符分割的地址
        if '[' in row[image_path_feature] and ']' in row[image_path_feature]:
            image_address = eval(row[image_path_feature])[0]
        else:
            image_address = row[image_path_feature].split('\n')[0]

        image_address = image_address.replace("\\", "/")

        try:
            if image_type == 'path':
                image_path = image_address
                img = image.Image(image_path)
                ws.add_image(img, f'{put_image_feature}{index+2}')
            elif image_type == 'url':
                image_url = image_address
                image_data = requests.get(image_url).content
                img = image.Image(BytesIO(image_data))
                ws.add_image(img, f'{put_image_feature}{index + 2}')
            else:
                print(f'image_type error，must in [url, type], now is {image_type}')
        except Exception as e:
            traceback.print_exc()
            print('错误行:', index)

    # 保存Excel文件
    wb.save(save_path)


if __name__ == '__main__':
    put_image_to_excel(
        excel_path='/Users/yangchengcheng/Documents/workspace/api_online/临时项目/影像打标-0521/data/0528/照片书-抽样-output-format-sheet1.xlsx',
        image_path_feature='url',  # 字段名称
        put_image_feature='X',  # 需要放置图片的字段的索引
        image_type='url',  # 图片类型 url or path
        top_row_number=20  # 设置读取的行数,-1 代表全部行
    )