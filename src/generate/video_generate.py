import src.core.publishBase as pb
import time
from PIL import Image
import configparser
import os
import random
import requests
import json
import shutil

# 基本信息
# 视频存放路径
from src.utils import openai_utils
from src.config import config_loader

VIDEO_ROOT = "../../input/video"

TITLE_PROMPT_FILE = "../../input/title_prompt.txt"
CONTENT_PROMPT_FILE = "../../input/content_prompt.txt"

TITLE_PIC_FILE = "../../input/title.png"


def generate_output_videos(files):
    file = os.path.join(VIDEO_ROOT, files[(pb.max_count - 1) % len(files)])
    output_file = os.path.join(pb.OUTPUT_ROOT, "%d-vi.mp4" % pb.max_count)
    shutil.copy(file, output_file)


def load_title_content_prompts():
    with open(TITLE_PROMPT_FILE, encoding="utf8") as file: title_prompt = file.read()
    with open(CONTENT_PROMPT_FILE, encoding="utf8") as file: content_prompt = file.read()

    return title_prompt, content_prompt

def generate_title_content(title_prompt, content_prompt):
    output_title = openai_utils.generate_completion(title_prompt)
    output_content = openai_utils.generate_completion(content_prompt)

    return output_title, output_content


def save_title_content(title, content):
    output_title_path = os.path.join(pb.OUTPUT_ROOT, "%d-title.txt" % pb.count)
    with open(output_title_path, "w", encoding="utf8") as file: file.write(title)

    output_content_path = os.path.join(pb.OUTPUT_ROOT, "%d-content.txt" % pb.count)
    with open(output_content_path, "w", encoding="utf8") as file: file.write(content)


def upload_generation(title_prompt, content_prompt, title, content):
    #TODO: 上传Generation
    pass


def generate():
    pb.max_count += 1
    print("Start generate: %d" % pb.max_count)

    generate_output_videos(os.listdir(VIDEO_ROOT))
    title_prompt, content_prompt = load_title_content_prompts()
    output_title, output_content = generate_title_content(title_prompt, content_prompt)
    save_title_content(output_title, output_content)

    pb.set_count('max_count', pb.max_count)

    print("End generate: %s: %s" % (output_title, output_content))


def main():
    pb.get_count()
    while pb.max_count < max_count:
        generate()
        time.sleep(interval)


if __name__ == '__main__':
    interval = config_loader.get_int('Generate', 'interval')
    pic_count = config_loader.get_int('Generate', 'pic_count')
    max_count = config_loader.get_int('Generate', 'max_count')
    pic_mode = config_loader.get_enum('Generate', 'pic_mode')
    use_title = config_loader.get_bool('Generate', 'use_title')

    main()

