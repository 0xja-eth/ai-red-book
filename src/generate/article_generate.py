import os
import random

from PIL import Image

import src.utils.image_utils as image
from src.core.generator import Generator, GenerateType, INPUT_ROOT

# 基本信息
# 图片存放路径
PICTURE_ROOT = os.path.join(INPUT_ROOT, "picture")
TITLE_PIC_FILE = os.path.join(INPUT_ROOT, "title.png")


class ArticleGenerator(Generator):

  def __init__(self):
    super().__init__(GenerateType.Article)

  # region Config

  def pic_count(self):
    return self.load_config("pic_count", "int")

  def pic_mode(self):
    return self.load_config("pic_mode", "enum")

  def use_title(self):
    return self.load_config("use_title", "bool")

  def is_repeatable(self):
    return self.load_config("is_repeatable", "bool")

  # endregion

  def flatten(self, lst):
    flat_list = []
    for item in lst:
      if isinstance(item, list):
        flat_list.extend(self.flatten(item))
      else:
        flat_list.append(item)
    return flat_list

  def filter_files(self, files, count):
    if not self.is_repeatable():
      ids = self.generation_ids()
      urls = [os.path.normpath(url) for url in self.flatten(
        [self.get_output(id).urls for id in ids if self.get_output(id) is not None]
      )]
      new_files = [file for file in files if file not in urls]
      if len(new_files) >= count: files = new_files

    if len(files) < 9 or self.is_repeatable():
      files = random.choices(files, k=count)
    else:
      files = random.sample(files, k=count)

    return files

  def generate_9_pic(self, files, output_file):

    files = self.filter_files(files, 9)

    # if not self.is_repeatable():
    #   ids = self.generation_ids()
    #   urls = [os.path.normpath(url) for url in self.flatten(
    #     [self.get_output(id).urls for id in ids]
    #   )]
    #   new_files = [file for file in files if file not in urls]
    #   if len(new_files) >= 9: files = new_files
    #
    # if len(files) < 9 or self.is_repeatable():
    #   files = random.choices(files, k=9)
    # else:
    #   files = random.sample(files, k=9)

    output_image = image.generate_9_pic(files)

    if self.use_title(): output_image = image.add_pic_title(output_image, TITLE_PIC_FILE)

    output_image.save(output_file)

    return output_file

  def generate_4_pic(self, files, output_file):

    files = self.filter_files(files, 4)

    # if not self.is_repeatable():
    #   ids = self.generation_ids()
    #   urls = [os.path.normpath(url) for url in self.flatten(
    #     [self.get_output(id).urls for id in ids]
    #   )]
    #   new_files = [file for file in files if file not in urls]
    #   if len(new_files) >= 4: files = new_files
    #
    # if len(files) < 4 or self.is_repeatable():
    #   files = random.choices(files, k=4)
    # else:
    #   files = random.sample(files, k=4)

    output_image = image.generate_4_pic(files)

    if self.use_title(): output_image = image.add_pic_title(output_image, TITLE_PIC_FILE)

    output_image.save(output_file)

    return output_file

  def generate_single(self, files, count):

    res = self.filter_files(files, count)

    # if not self.is_repeatable():
    #   ids = self.generation_ids()
    #   urls = [os.path.normpath(url) for url in self.flatten(
    #     [self.get_output(id).urls for id in ids]
    #   )]
    #   new_files = [file for file in files if file not in urls]
    #   if len(new_files) >= count: files = new_files
    #
    # if len(files) < count or self.is_repeatable():
    #   res = random.choices(files, k=count)
    # else:
    #   res = random.sample(files, k=count)

    # res = [os.path.join(PICTURE_ROOT, file) for file in sampled_files]

    if self.use_title():
      for i in range(len(res)):
        if self.pic_count() == 1:
          output_file = os.path.join(self.output_dir(), "%d-pic.jpg" % self.generating_count)
        else:
          output_file = os.path.join(self.output_dir(), "%d-pic-%d.jpg" % (self.generating_count, i + 1))

        file = res[i]

        output_image = Image.open(file)
        output_image = image.add_pic_title(output_image, TITLE_PIC_FILE)
        output_image.save(output_file)

        res[i] = output_file

    return res

  def _generate_media(self) -> list:
    files = os.listdir(PICTURE_ROOT)
    files = [os.path.normpath(os.path.join(PICTURE_ROOT, file)) for file in files]

    if self.pic_mode() == "single":
      urls = self.generate_single(files, self.pic_count())
    else:
      urls = []

      for i in range(self.pic_count()):
        if self.pic_count() == 1:
          output_file = os.path.join(self.output_dir(), "%d-pic.jpg" % self.generating_count)
        else:
          output_file = os.path.join(self.output_dir(), "%d-pic-%d.jpg" % (self.generating_count, i + 1))

        if self.pic_mode() == "9_pic":
          output_file = self.generate_9_pic(files, output_file)
        elif self.pic_mode() == "4_pic":
          output_file = self.generate_4_pic(files, output_file)

        urls.append(output_file)

    return urls


generator = ArticleGenerator()

# if __name__ == '__main__':
#     generator.multi_generate()
