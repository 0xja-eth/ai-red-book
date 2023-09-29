import src.core.publishBase as pb
import src.utils.image_utils as image
from PIL import Image
import os
import random

from src.config import config_loader
from src.core.generator import Generator, GenerateType

# 基本信息
# 图片存放路径
PICTURE_ROOT = config_loader.file("./input/picture")

TITLE_PROMPT_FILE = config_loader.file("./input/title_prompt.txt")
CONTENT_PROMPT_FILE = config_loader.file("./input/content_prompt.txt")

TITLE_PIC_FILE = config_loader.file("./input/title.png")

OUTPUT_ROOT = config_loader.file("./output/article")

class ArticleGenerator(Generator):

  def __init__(self):
    super().__init__(GenerateType.Article)

  # region Config

  def pic_count(self): return self.load_config("pic_count", "int")
  def pic_mode(self): return self.load_config("pic_mode", "enum")
  def use_title(self): return self.load_config("use_title", "bool")
  def is_repeatable(self): return self.load_config("is_repeatable", "bool")

  # endregion

  def generate_9_pic(self, files, output_file):
    files = random.sample(files, k=9)
    files = [os.path.join(PICTURE_ROOT, file) for file in files]
    output_image = image.generate_9_pic(files)

    if self.use_title(): output_image = image.add_pic_title(output_image, TITLE_PIC_FILE)

    output_image.save(output_file)

    return output_file

  def generate_4_pic(self, files, output_file):
    if not self.is_repeatable():
      ids = self.generation_ids()
      urls = [url for url in [self.get_output(id).urls for id in ids]]
      files = [file for file in files if file not in urls]

    files = random.sample(files, k=4)
    files = [os.path.join(PICTURE_ROOT, file) for file in files]
    output_image = image.generate_4_pic(files)

    if self.use_title(): output_image = image.add_pic_title(output_image, TITLE_PIC_FILE)

    output_image.save(output_file)

    return output_file

  def generate_single(self, files, output_file):
    if not self.is_repeatable():
      ids = self.generation_ids()
      urls = [url for url in [self.get_output(id).urls for id in ids]]
      files = [file for file in files if file not in urls]

    file = os.path.join(PICTURE_ROOT, random.choice(files))

    if self.use_title():
      output_image = Image.open(file)
      output_image = image.add_pic_title(output_image, TITLE_PIC_FILE)
      output_image.save(output_file)

      return output_file
    else:
      return file

  def _generate_media(self) -> list:
    files = os.listdir(PICTURE_ROOT)

    urls = []

    for i in range(self.pic_count()):
      if self.pic_count() == 1:
        output_file = os.path.join(OUTPUT_ROOT, "%d-pic.jpg" % self.gen_count())
      else:
        output_file = os.path.join(OUTPUT_ROOT, "%d-pic-%d.jpg" % (self.gen_count(), i + 1))

      if self.pic_mode() == "9_pic":
        output_file = self.generate_9_pic(files, output_file)
      elif self.pic_mode() == "4_pic":
        output_file = self.generate_4_pic(files, output_file)
      elif self.pic_mode() == "single":
        output_file = self.generate_single(files, output_file)

      urls.append(output_file)

    return urls
