
import asyncio
import openai
from PIL import Image
import configparser
import os
import random

# 基本信息
# 图片存放路径
PHOTO_ROOT = "./photo"

TITLE_PROMPT_FILE = "./title_prompt.txt"
CONTENT_PROMPT_FILE = "./content_prompt.txt"
COUNT_FILE = "./count.txt"

OUTPUT_ROOT = "./output"

# 读取配置文件
config = configparser.ConfigParser()
config.read('config.ini')

with open(COUNT_FILE, encoding="utf8") as c_file:
    count = int(c_file.read())


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


async def generate_completion(prompt):
    print("generating completion: %s" % prompt)

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=2048,
    )

    message = response.choices[0].text.replace(" ", "").strip()
    print("generated completion: %s" % message)

    return message


async def main(num):
    global count

    for i in range(0, num):
        count += 1

        openai.api_key = config.get('API', 'openai_key')

        files = os.listdir(PHOTO_ROOT)
        files = random.choices(files, k=9)
        files = [os.path.join(PHOTO_ROOT, file) for file in files]
        output_image = generate_9_pic(files)

        output_image_path = os.path.join(OUTPUT_ROOT, "%d-pic.jpg" % count)
        output_image.save(output_image_path)

        with open(TITLE_PROMPT_FILE, encoding="utf8") as file:
            prompt = file.read()

        output_title = await generate_completion(prompt)
        output_title_path = os.path.join(OUTPUT_ROOT, "%d-title.txt" % count)

        with open(output_title_path, "w", encoding="utf8") as file:
            file.write(output_title)

        with open(CONTENT_PROMPT_FILE, encoding="utf8") as file:
            prompt = file.read()

        output_content = await generate_completion(prompt % output_title)
        output_content_path = os.path.join(OUTPUT_ROOT, "%d-content.txt" % count)

        with open(output_content_path, "w", encoding="utf8") as file:
            file.write(output_content)

        with open(COUNT_FILE, "w", encoding="utf8") as file:
            file.write(str(count))


if __name__ == '__main__':
    asyncio.run(main(1))


