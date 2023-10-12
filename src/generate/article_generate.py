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

    def generate_9_pic(self, files, output_file, is_repeatable):

        if len(files) < 9 or is_repeatable:
            files = random.choices(files, k=9)
        else:
            files = random.sample(files, k=9)
        files = [os.path.join(PICTURE_ROOT, file) for file in files]
        output_image = image.generate_9_pic(files)

        if self.use_title(): output_image = image.add_pic_title(output_image, TITLE_PIC_FILE)

        output_image.save(output_file)

        return output_file

    def generate_4_pic(self, files, output_file, is_repeatable):
        if not self.is_repeatable():
            ids = self.generation_ids()
            urls = [url for url in [self.get_output(id).urls for id in ids]]
            files = [file for file in files if file not in urls]

        if len(files) < 4 or is_repeatable:
            files = random.choices(files, k=4)
        else:
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
                output_file = os.path.join(self.output_dir(), "%d-pic.jpg" % self.generating_count)
            else:
                output_file = os.path.join(self.output_dir(), "%d-pic-%d.jpg" % (self.generating_count, i + 1))

            if self.pic_mode() == "9_pic":
                output_file = self.generate_9_pic(files, output_file, self.is_repeatable())
            elif self.pic_mode() == "4_pic":
                output_file = self.generate_4_pic(files, output_file, self.is_repeatable())
            elif self.pic_mode() == "single":
                output_file = self.generate_single(files, output_file)

            urls.append(output_file)

        return urls


generator = ArticleGenerator()

# if __name__ == '__main__':
#     generator.multi_generate()
