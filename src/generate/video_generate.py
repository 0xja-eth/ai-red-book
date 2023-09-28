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

