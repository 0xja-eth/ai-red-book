import core.publishBase as pb
import time
from PIL import Image
import configparser
import os
import random
import requests
import json
import shutil

# 基本信息
# 图片存放路径
VIDEO_ROOT = "../input/video"

TITLE_PROMPT_FILE = "./title_prompt.txt"
CONTENT_PROMPT_FILE = "./content_prompt.txt"

TITLE_PIC_FILE = "./title.png"




# 自动铺满
def resize_image(image, target_width, target_height):
    # 获取原始图片的宽度和高度
    width, height = image.size

    # 计算缩放比例
    width_ratio = target_width / width
    height_ratio = target_height / height
    ratio = max(width_ratio, height_ratio)

    # 计算调整后的图片尺寸
    new_width = int(width * ratio)
    new_height = int(height * ratio)

    # 缩放图片
    resized_image = image.resize((new_width, new_height), Image.LANCZOS)

    # 裁剪图片到目标尺寸
    left = (new_width - target_width) // 2
    top = (new_height - target_height) // 2
    right = left + target_width
    bottom = top + target_height
    resized_image = resized_image.crop((left, top, right, bottom))

    return resized_image


# 生成九宫格
def generate_9_pic(files):
    images = [Image.open(file) for file in files]

    # 获取图片的宽高（第一张图为准）
    image_width, image_height = images[0].size

    # 创建新图片，尺寸为3倍的宽度和高度
    result_width = image_width * 3
    result_height = image_height * 3
    result_image = Image.new('RGB', (result_width, result_height))

    # 将九张图片按照九宫格排列拼接到新图片上
    for i in range(3):
        for j in range(3):
            resized_image = resize_image(images[i * 3 + j], image_width, image_height)
            result_image.paste(resized_image, (j * image_width, i * image_height))

    return result_image


# 生成图片标题
def add_pic_title(image):
    width, height = image.size

    title_img = Image.open(TITLE_PIC_FILE)
    title_width, title_height = title_img.size

    title_x, title_y = (width - title_width) // 2, (height - title_height) // 2

    image.paste(title_img, (title_x, title_y), mask=title_img)

    return image


def generate():

    pb.max_count += 1

    print("Start generate: %d" % pb.max_count)

    files = os.listdir(VIDEO_ROOT)
    file = os.path.join(VIDEO_ROOT, files[(pb.max_count - 1) % len(files)])
    output_file = os.path.join(pb.OUTPUT_ROOT, "%d-vi.mp4" % pb.max_count)

    shutil.copy(file, output_file)

    with open(TITLE_PROMPT_FILE, encoding="utf8") as file:
        title_prompt = file.read()

    with open(CONTENT_PROMPT_FILE, encoding="utf8") as file:
        content_prompt = file.read()

    url = "%s/generate" % host
    headers = {'Content-Type': 'application/json'}
    data = {'api_key': api_key, 'title_prompt': title_prompt, 'content_prompt': content_prompt}

    response = requests.post(url, headers=headers, data=json.dumps(data))
    res_json = response.json()

    output_title = res_json["title"]
    output_content = res_json["content"]

    output_title_path = os.path.join(pb.OUTPUT_ROOT, "%d-title.txt" % pb.count)
    with open(output_title_path, "w", encoding="utf8") as file:
        file.write(output_title)

    output_content_path = os.path.join(pb.OUTPUT_ROOT, "%d-content.txt" % pb.count)
    with open(output_content_path, "w", encoding="utf8") as file:
        file.write(output_content)

    pb.set_count('max_count', pb.max_count)

    print("End generate: %s: %s" % (output_title, output_content))


def main():
    pb.get_count()
    while pb.max_count < max_count:
        generate()
        time.sleep(interval)


if __name__ == '__main__':
    host = pb.config.get('Generate', 'host')
    api_key = pb.config.get('Generate', 'openai_key')
    interval = int(pb.config.get('Generate', 'interval'))
    max_count = int(pb.config.get('Generate', 'max_count'))

    main()

