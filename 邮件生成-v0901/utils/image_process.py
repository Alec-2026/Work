import requests
import base64
from PIL import Image
from io import BytesIO
import requests
from PIL import Image
from io import BytesIO
import base64


def download_image(url, output_filename):
    try:
        # 发送HTTP请求获取图片内容
        response = requests.get(url, stream=True)

        # 检查请求是否成功
        if response.status_code == 200:
            # 打开文件并写入图片内容
            with open(output_filename, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            print(f"图片已成功下载并保存为 {output_filename}")
        else:
            print(f"无法下载图片，HTTP状态码: {response.status_code}")

    except Exception as e:
        print(f"下载图片时出现错误: {e}")



def encode_image_from_url(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        image_base64 = base64.b64encode(response.content).decode('utf-8')
        return image_base64
    else:
        print(f"Failed to retrieve image. Status code: {response.status_code}")
        return None



def get_image_info(url):
    # 获取图片的响应内容
    response = requests.get(url)

    if response.status_code == 200:
        # 获取文件大小（单位：字节）
        size_bytes = len(response.content)
        size_kb = size_bytes / 1024
        size_mb = size_kb / 1024

        # 使用 Pillow 读取图片尺寸
        image = Image.open(BytesIO(response.content))
        width, height = image.size

        return {
            'size_bytes': size_bytes,
            'size_kb': round(size_kb, 2),
            'size_mb': round(size_mb, 2),
            'width': width,
            'height': height
        }
    else:
        return f"Failed to load image, status code: {response.status_code}"


def is_valid_image(image_url):
    """
    检测是否是有效图片，要求width和height均>=10
    :param image_url:
    :return:
    """
    image_info = get_image_info(image_url)
    if image_info['width'] < 10 or image_info['height'] < 10:
        return False
    return True


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
            response = requests.get(image, timeout=100)
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


def image_compression_by_url(image_url):
    """
    自动压缩图片，确保图片的像素数不超过1280个token（每个token是28*28像素）
    return base64 str
    """
    max_pixels = 1280 * 28 * 28  # 计算最大的像素数量，图片最多是1280个token，每28*28像素是一个token
    try:
        # 获取图片响应
        response = requests.get(image_url)
        if response.status_code == 200:
            # 打开图片
            img = Image.open(BytesIO(response.content))
            img.load()

            # 获取原始尺寸
            width, height = img.size
            current_pixels = width * height
            print(f'原始像素数: {current_pixels}, width: {width}, height: {height}', )

            if current_pixels > max_pixels:
                # 计算压缩比例
                ratio = (max_pixels / current_pixels) ** 0.5
                new_width = int(width * ratio)
                new_height = int(height * ratio)

                # 调整图片大小，使用 Resampling.LANCZOS 替代 ANTIALIAS
                resized_image = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                # 如果图像是RGBA模式，则转换为RGB模式
                if resized_image.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', resized_image.size, (255, 255, 255))
                    background.paste(resized_image, mask=resized_image.split()[
                        3] if resized_image.mode == 'RGBA' else None)  # 3 is the alpha channel
                    resized_image = background

                # 将调整后的图像保存到BytesIO
                buffered = BytesIO()
                resized_image.save(buffered, format="JPEG", quality=95)

                new_width, new_height = resized_image.size
                new_current_pixels = width * height
                print(f'图片压缩比例: {ratio}, 新像素数: {new_current_pixels}, 新width: {new_width}, 新height: {new_height}')

                # 将图片内容转换为base64编码
                return base64.b64encode(buffered.getvalue()).decode('utf-8')
            else:
                print(f'图片像素数小于目标元素数量{max_pixels}，占比: {round(current_pixels/max_pixels, 4)*100}%, 无需压缩')
            # 将原始图片内容转换为base64编码
            return base64.b64encode(response.content).decode('utf-8')
        else:
            print(f"无法下载图片，HTTP状态码: {response.status_code}")
            return None
    except Exception as e:
        print(f"压缩图片时出现错误: {e}")
        return None

def image_to_base64(image_path: str) -> str:
    """
    将指定路径的图片转换为Base64编码字符串

    Args:
        image_path: 图片文件的本地路径（绝对路径或相对路径）

    Returns:
        完整的Base64编码字符串（包含图片格式标识，可直接用于HTML、JSON等场景）
    """
    # 1. 以二进制只读模式打开图片文件（rb模式是处理二进制文件的关键）
    with open(image_path, 'rb') as image_file:
        # 2. 读取图片二进制数据
        image_binary_data = image_file.read()

        # 3. 使用base64.b64encode()编码二进制数据，返回bytes类型结果
        base64_bytes = base64.b64encode(image_binary_data)

        # 4. 将bytes类型的编码结果解码为utf-8格式的字符串（便于存储和传输）
        base64_str = base64_bytes.decode('utf-8')


    return base64_str


def image_compression_by_path(image_path):
    """
    自动压缩图片，确保图片的像素数不超过1280个token（每个token是28*28像素）
    return base64 str
    """
    max_pixels = 1280 * 28 * 28  # 计算最大的像素数量，图片最多是1280个token，每28*28像素是一个token
    try:
        # 获取图片响应
        # response = requests.get(image_url)
        # if response.status_code == 200:
        #     # 打开图片
        #     img = Image.open(BytesIO(response.content))
        #     img.load()

        if True:
            img = Image.open(image_path)
            img.load()

            # 获取原始尺寸
            width, height = img.size
            current_pixels = width * height
            print(f'原始像素数: {current_pixels}, width: {width}, height: {height}', )

            if current_pixels > max_pixels:
                # 计算压缩比例
                ratio = (max_pixels / current_pixels) ** 0.5
                new_width = int(width * ratio)
                new_height = int(height * ratio)

                # 调整图片大小，使用 Resampling.LANCZOS 替代 ANTIALIAS
                resized_image = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                # 如果图像是RGBA模式，则转换为RGB模式
                if resized_image.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', resized_image.size, (255, 255, 255))
                    background.paste(resized_image, mask=resized_image.split()[
                        3] if resized_image.mode == 'RGBA' else None)  # 3 is the alpha channel
                    resized_image = background

                # 将调整后的图像保存到BytesIO
                buffered = BytesIO()
                resized_image.save(buffered, format="JPEG", quality=95)

                new_width, new_height = resized_image.size
                new_current_pixels = width * height
                print(f'图片压缩比例: {ratio}, 新像素数: {new_current_pixels}, 新width: {new_width}, 新height: {new_height}')

                # 将图片内容转换为base64编码
                return base64.b64encode(buffered.getvalue()).decode('utf-8')
            else:
                print(f'图片像素数小于目标元素数量{max_pixels}，占比: {round(current_pixels/max_pixels, 4)*100}%, 无需压缩')


            return image_to_base64(image_path)

    except Exception as e:
        print(f"压缩图片时出现错误: {e}")
        return None



def image_compression(image_address, image_type='url'):
    if image_type == 'url':
        return image_compression_by_url(image_address)
    elif image_type == 'path':
        return image_compression_by_path(image_address)
    else:
        return None





if __name__ == '__main__':
    """自动压缩图片功能测试"""
    # url = 'https://ddiy.36588.com.cn/diypreview/downproduct/2732691778/thirdpart/taobao/2025-10-05/2404488900235429386-25-10-05-175738-0229/12寸双面水晶照片书32p_2732691778/1612寸双面水晶照片书32p_2732691778_第16幅(15)_共17.jpg'
    # url = 'http://10.168.20.103/images/ithumb//2025/2025-04-05/东讯/17/2520801516195139284/2301a1cd07524becb3c803a49e41a9e7.jpg'
    url = '/Users/yangchengcheng/Documents/workspace/api_online/临时项目/不干胶全切稿件打标/data/全切跑稿件/image001.png'
    res = image_compression(url, 'path')
    print(res)

    """使用示例：图片下载和压缩"""
    # image_url = "https://scontent-hkg1-1.xx.fbcdn.net/v/t39.35426-6/473678462_1116247649773125_5700045378951203118_n.jpg?stp=dst-jpg_s600x600_tt6&_nc_cat=101&ccb=1-7&_nc_sid=c53f8f&_nc_ohc=1nR8nPNmGf4Q7kNvgFnn1d2&_nc_oc=AdliOVJkrC72FAp1cWlIXdQl4tWvyOaOEJKVqw1iecwrCcnciZqtHX6f3DlEiWV7ovA&_nc_zt=14&_nc_ht=scontent-hkg1-1.xx&_nc_gid=hTSXhrvquON7qs_ODTZUdA&oh=00_AYFS4Un_2tdhzi6fDPLPYqAxBZ0JBNQT1OUzUMQcJFbVKg&oe=67F12802"
    # output_file = "images/downloaded_image.jpg"
    # download_image(image_url, output_file)
    #
    # print(encode_image_from_url(
    #     'https://scontent-hkg1-1.xx.fbcdn.net/v/t39.35426-6/481993655_934790512138733_6119369493273913304_n.jpg?stp=dst-jpg_s600x600_tt6&_nc_cat=109&ccb=1-7&_nc_sid=c53f8f&_nc_ohc=z2OnJ_KFrB8Q7kNvgEC4CMA&_nc_oc=Adnpl_JrGcn3RFC9ci9TE5GDzTKGJXT5QNkfiGu6p9afFAJZ3LONOID4mSTifkFv4DA&_nc_zt=14&_nc_ht=scontent-hkg1-1.xx&_nc_gid=y_8E03PKkmbIDaAgyC_yQQ&oh=00_AYErmq4uuOrebvFBHOsXBqYDo60iByVFpW8cr-ubntEkgg&oe=67F12812'
    # ))