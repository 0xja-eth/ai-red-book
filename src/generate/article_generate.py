import src.core.publishBase as pb
import src.utils.image_utils as image
import time
from PIL import Image
import os
import random
import shutil

from src.config import config_loader
from src.utils import openai_utils

# 基本信息
# 图片存放路径
PICTURE_ROOT = "../input/picture"

TITLE_PROMPT_FILE = "../input/title_prompt.txt"
CONTENT_PROMPT_FILE = "../input/content_prompt.txt"

TITLE_PIC_FILE = "../input/title.png"

OUTPUT_ROOT = "../output/article"

def generate_9_pic(files, output_file):
  files = random.sample(files, k=9)
  files = [os.path.join(PICTURE_ROOT, file) for file in files]
  output_image = image.generate_9_pic(files)

  if use_title: output_image = image.add_pic_title(output_image, TITLE_PIC_FILE)

  output_image.save(output_file)

def generate_4_pic(files, output_file):
  files = random.sample(files, k=4)
  files = [os.path.join(PICTURE_ROOT, file) for file in files]
  output_image = image.generate_4_pic(files)

  if use_title: output_image = image.add_pic_title(output_image, TITLE_PIC_FILE)

  output_image.save(output_file)

def generate_single(files, output_file):
  file = os.path.join(PICTURE_ROOT, random.choice(files))

  if use_title:
    output_image = Image.open(file)
    output_image = image.add_pic_title(output_image, TITLE_PIC_FILE)
    output_image.save(output_file)
  else:
    shutil.copy(file, output_file)

def generate_output_images(files):
  for i in range(pic_count):
    if pic_count == 1: output_file = os.path.join(OUTPUT_ROOT, "%d-pic.jpg" % pb.max_count)
    else: output_file = os.path.join(OUTPUT_ROOT, "%d-pic-%d.jpg" % (pb.max_count, i + 1))

    if pic_mode == "9_pic": generate_9_pic(files, output_file)
    elif pic_mode == "4_pic": generate_4_pic(files, output_file)
    elif pic_mode == "single": generate_single(files, output_file)

def load_title_content_prompts():
  with open(TITLE_PROMPT_FILE, encoding="utf8") as file: title_prompt = file.read()
  with open(CONTENT_PROMPT_FILE, encoding="utf8") as file: content_prompt = file.read()

  return title_prompt, content_prompt

def generate_title_content(title_prompt, content_prompt):
  title = openai_utils.generate_completion(title_prompt)
  content = openai_utils.generate_completion(content_prompt % title)

  return title, content

def save_title_content(title, content):
  output_title_path = os.path.join(OUTPUT_ROOT, "%d-title.txt" % pb.max_count)
  with open(output_title_path, "w", encoding="utf8") as file: file.write(title)

  output_content_path = os.path.join(OUTPUT_ROOT, "%d-content.txt" % pb.max_count)
  with open(output_content_path, "w", encoding="utf8") as file: file.write(content)

def upload_generation(title_prompt, content_prompt, title, content):
  # TODO: 上传Generation
  pass

def generate():
  pb.max_count += 1
  print("Start generate: %d" % pb.max_count)

  generate_output_images(os.listdir(PICTURE_ROOT))

  title_prompt, content_prompt = load_title_content_prompts()
  title, content = generate_title_content(title_prompt, content_prompt)
  upload_generation(title_prompt, content_prompt, title, content)
  save_title_content(title, content)

  pb.set_count('max_count', pb.max_count)

  print("End generate: %s: %s" % (title, content))

def main():
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

