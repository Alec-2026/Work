import os.path
import traceback
from concurrent.futures import ThreadPoolExecutor
import requests
from openai import OpenAI
import concurrent.futures
import base64
from io import BytesIO
from PIL import Image
from operator import itemgetter
import pandas as pd
from openpyxl import load_workbook
from tqdm import tqdm
from openpyxl.drawing import image
import numpy as np
import configparser
import http.client
import json
import emoji


def get_website_info_by_request(web_url):
    try:
        headers = {"Content-Type": "application/json"}
        url = f'http://47.251.75.225:5005/get_website_content'
        data = {'url': web_url}
        response = requests.post(url, headers=headers, data=json.dumps(data)).json()
        return response
    except Exception as e:
        return {'code': 0, 'model_response': '无官网信息', 'info': f'failed: {str(repr(e))}'}


def search_by_google(content):
    try:
        conn = http.client.HTTPSConnection("google.serper.dev")
        payload = json.dumps({"q": content})
        headers = {
            'X-API-KEY': '5e043783e92b5654557e5c285dd1657c54a2cc2d',
            'Content-Type': 'application/json'
        }
        conn.request("POST", "/search", payload, headers)
        res = conn.getresponse()
        data = res.read()
        return data.decode("utf-8")
    except Exception as e:
        return '无搜索结果'


def encode_image_from_url(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        image_base64 = base64.b64encode(response.content).decode('utf-8')
        return image_base64
    else:
        print(f"Failed to retrieve image. Status code: {response.status_code}")
        return None


def encode_image_from_path(image_path):
    try:
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
            base64_encoded = base64.b64encode(image_data)
            return base64_encoded.decode('utf-8')
    except Exception as e:
        print(f"Failed to encode image. Exception: {e}")
        return ''


def get_prompt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content


# 调用模型函数
def chat_with_llm(url, model_path, messages, api_key='EMPTY'):
    openai_api_key = api_key
    openai_api_base = url

    client = OpenAI(
        api_key=openai_api_key,
        base_url=openai_api_base,
    )

    response = client.chat.completions.create(
        model=model_path,
        messages=messages,
        temperature=0.1,
        seed=128,
        max_tokens=2000,
    )

    return response


# 使用多线程的方式给大模型发送消息
def chat_with_llm_thread_multi(url, model_path, messages_list, api_key='EMPTY', thread_num=4):
    """
    messages_list: 消息队列
    demo：
    [
        [{'role':'user', 'content': '你好'}],
        [{'role':'user', 'content': '你叫什么'}],
        [{'role':'user', 'content': '你能帮我做什么'}]
    ]
    """
    # 使用多线程的方式调用模型，获取响应结果
    def chat_with_llm_single(mes, index):
        client = OpenAI(api_key=api_key, base_url=url)
        try:
            response = client.chat.completions.create(
                model=model_path,
                messages=mes,
                temperature=0,
                seed=128,
            ).choices[0].message.content
        except Exception as e:
            print(f'模型调用出错:{repr(e)}')
            response = None
        return index, mes, response

    result_dict = {}
    with concurrent.futures.ThreadPoolExecutor(thread_num) as executor:
        futures = [executor.submit(chat_with_llm_single, messages_list[i], i) for i in range(len(messages_list))]
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(messages_list), desc='LLM调用进度: '):
            try:
                customer, message, response = future.result()
                result_dict[customer] = response
            except Exception as e:
                print(f'llm 推理错误: {repr(e)}')

    sorted_dict = dict(sorted(result_dict.items()))

    result_list = []
    for _, value in sorted_dict.items():
        result_list.append(value)
    return result_list


# 将两张图片拼接为一张图片
def concatenate_images(base64_image1, base64_image2, direction='horizontal', border_width=10):
    def base64_to_image(base64_string):
        # 解码Base64字符串为字节流
        img_data = base64.b64decode(base64_string.split(',')[1] if ',' in base64_string else base64_string)
        # 创建BytesIO对象并读取字节流为Image对象
        return Image.open(BytesIO(img_data)).convert("RGBA")

        # 解码Base64图片字符串

    img1 = base64_to_image(base64_image1)
    img2 = base64_to_image(base64_image2)

    # 获取图片尺寸
    width1, height1 = img1.size
    width2, height2 = img2.size

    # 创建一个新的空白图像用于存放拼接结果
    if direction == 'horizontal':
        total_width = width1 + border_width + width2
        max_height = max(height1, height2)
        new_img = Image.new("RGBA", (total_width, max_height), (0, 0, 0, 0))  # 透明背景
        new_img.paste(img1, (0, 0))
        new_img.paste(img2, (width1 + border_width, 0))
    elif direction == 'vertical':
        max_width = max(width1, width2)
        total_height = height1 + border_width + height2
        new_img = Image.new("RGBA", (max_width, total_height), (0, 0, 0, 0))  # 透明背景
        new_img.paste(img1, (0, 0))
        new_img.paste(img2, (0, height1 + border_width))
    else:
        raise ValueError("direction must be 'horizontal' or 'vertical'")

    # 将新图像保存到BytesIO对象中
    output_buffer = BytesIO()
    new_img.save(output_buffer, format='PNG')
    byte_data = output_buffer.getvalue()
    output_buffer.close()

    # 编码为Base64字符串
    base64_encoded_result = base64.b64encode(byte_data).decode('utf-8')

    return base64_encoded_result


# 调整图片大小
def resize_image(image, resize_ratio=0.3, image_type='url'):
    """
    根据提供的图片链接下载图片，并按照指定的比例调整大小。

    参数:
    image_url : str
        图片的URL地址。
    resize_ratio : float
        需要减少的比例，默认是0.3（即30%）。

    返回值:
    tuple
        一个包含两个元素的元组：
        - resized_image : PIL.Image.Image
          调整大小后的PIL图像对象。
        - img_base64 : str
          图像的Base64编码字符串。
    """
    # 下载图片
    try:
        if image_type == 'url':
            response = requests.get(image)
            img = Image.open(BytesIO(response.content))
            img.load()
        elif image_type == 'path':
            img = Image.open(image)
            img.load()
        else:
            print('image type error')
            return None

        # 获取原始尺寸
        original_size = img.size

        # 计算新的尺寸
        new_size = tuple(int(dim * (1 - resize_ratio)) for dim in original_size)

        # 调整图片大小，使用 Resampling.LANCZOS 替代 ANTIALIAS
        resized_image = img.resize(new_size, Image.Resampling.LANCZOS)

        # 如果图像是RGBA模式，则转换为RGB模式
        if resized_image.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', resized_image.size, (255, 255, 255))
            background.paste(resized_image, mask=resized_image.split()[
                3] if resized_image.mode == 'RGBA' else None)  # 3 is the alpha channel
            resized_image = background

        # 将调整后的图像保存为JPEG格式并转换为Base64编码
        buffered = BytesIO()
        resized_image.save(buffered, format="JPEG", quality=95)
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

        return resized_image, img_base64
    except Exception as e:
        return None, None


# 根据字典顺序排序
def sort_list(lt: list):
    tmp_dict = {}
    for x in lt:
        tmp_dict[x] = x.lower()
    sorted_dict_items = sorted(tmp_dict.items(), key=itemgetter(1))
    sorted_dict = dict(sorted_dict_items)
    return list(sorted_dict.keys())


# 对每个列表，添加空格直到它们的长度与最大长度相等
def equalize_multiple_lists(*lists):
    # 找出所有列表的最大长度
    max_length = max(len(lst) for lst in lists)

    # 对每个列表，添加空格直到它们的长度与最大长度相等
    for lst in lists:
        lst.extend([' '] * (max_length - len(lst)))

    return lists


# 多线程处理dataframe的row
def process_dataframe_multi_thread(df, process_row_function, max_workers=10):
    """
    多线程处理DataFrame的优化版本

    Args:
        df: 待处理的DataFrame
        process_row_function: 行处理函数，接收row对象作为参数
        max_workers: 最大线程数（默认10）

    Returns:
        list: 按原始索引顺序排列的处理结果列表
    """
    results = [None] * len(df)

    # 使用线程池处理所有行（不再分批）
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 创建任务字典（future对象到原始索引的映射）
        futures = {
            executor.submit(process_row_function, row): idx
            for idx, row in df.iterrows()
        }

        # 使用tqdm进度条监控处理进度
        for future in tqdm(futures, total=len(df), desc='多线程处理进度'):
            idx = futures[future]
            try:
                results[idx] = future.result()
            except Exception as e:
                print(f"处理行 {idx} 时出错: {e}")
                results[idx] = None  # 错误处理

    return results


# 将图片放置到Excel中
def put_image_to_excel(excel_path, image_path_feature, put_image_feature, image_type='path'):
    """
    将图片放置到excel中
    参数：
    excel_path: 原始excel的地址
    image_path_feature: 图片地址所在的列
    put_image_feature: 图片需要放到的列
    image_type: 图片地址的类型：path or url
    return: None，保存到excel中，原始excel地址加_image的后缀
    """
    df = pd.read_excel(excel_path)
    save_path = excel_path[:-5]+'_image'+'.xlsx'
    df.to_excel(save_path, sheet_name='sheet1', index=False)
    wb = load_workbook(save_path)
    ws = wb['sheet1']
    for index, row in tqdm(df.iterrows(), total=df.shape[0], desc='图片填充'):
        try:
            if image_type == 'path':
                image_path = row[image_path_feature].split('\n')[0]
                img = image.Image(image_path)
                ws.add_image(img, f'{put_image_feature}{index+2}')
            elif image_type == 'url':
                image_url = row[image_path_feature].split('\n')[0]
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


# 检测图片是否是一张白纸
def is_white_paper(base64_str, mean_threshold=240, std_threshold=10):
    # 解码 base64
    image_data = base64.b64decode(base64_str)
    image = Image.open(BytesIO(image_data))

    # 转换为灰度图
    gray = np.array(image.convert('L'))  # 'L' 表示灰度模式

    # 计算均值和标准差
    mean_value = np.mean(gray)
    std_value = np.std(gray)

    # 判断是否为白纸
    return mean_value >= mean_threshold and std_value <= std_threshold


def save_excel_by_sheet(df_list: list, sheet_name_list: list, file_path: str):
    df_list[0].to_excel(file_path, sheet_name=sheet_name_list[0], index=False)
    with pd.ExcelWriter(file_path, mode="a", engine="openpyxl", if_sheet_exists="new") as writer:
        for i in range(len(df_list)):
            if i == 0:
                continue
            else:
                df_list[i].to_excel(writer, sheet_name=sheet_name_list[i], index=False)


def contains_emoji(text):
    # 判断字符串中是否包含emogi表情
    return any(char in emoji.EMOJI_DATA for char in text)



if __name__ == '__main__':
    print(contains_emoji('hello world👋'))
    """
    图片放置到excel中测试
    """
    # put_image_to_excel(
    #     excel_path='data/独立站测试文件_output_format_google_output_deal.xlsx',
    #     image_path_feature='image',
    #     put_image_feature='K'
    # )

    """图片压缩函数测试"""
    # resized_img, _ = resize_image(
    #     'https://www.jiansheji.cn/dsthumb82/sdc_4035/sheji_wangkuo/data/【00订单文件】/2025-02-05/【Z平台自动下载】/Racetop_20240005752/缩略图/608b544e7f01430b88852bba0add4bdc.jpg',
    #     0.1,
    #     image_type='url'
    # )
    # resized_img.save("resized_image.jpg", quality=95)

    # # 拼接图片函数测试
    # url1 = 'https://diy.zheliyin.com/siteWeb/assets/resource/imgs/large/MXYZ-0006F218A4E34EFD863FBE8989320EA1.png'
    # url2 = 'https://diy.zheliyin.com/siteWeb/assets/resource/imgs/large/MXYZ-5470CD592FD1470490E64CBD6DDCEABF.png'
    # output_path = '/Users/yangchengcheng/Documents/workspace/train_model/智能设计/素材打标/data/tt/合并.png'
    # concatenated_img = concatenate_images(encode_image_from_url(url1), encode_image_from_url(url2), direction='vertical')
    # concatenated_img.save(output_path)
    # print(f"图片已保存到 {output_path}")

    # # 调用模型函数测试
    # messages = [{'role': 'user', 'content': '你和chatgpt有哪些区别'}]
    # response = chat_with_llm(
    #     url=service_dict[service_name]['url'],
    #     model_path=service_dict[service_name]['model'],
    #     messages=messages,
    #     api_key=service_dict[service_name]['api_key'],
    # ).choices[0].message.content
    # print(response)

    # # # 多线程测试
    # import pandas as pd
    # df = pd.read_excel('data/独立站测试文件.xlsx')
    # def process_row(row):
    #     return row['image']
    # res = process_dataframe_multi_thread(df, process_row, max_workers=2)
    # print(res)
