import os

from src.core.generator import Generator, GenerateType
from src.config import config_loader

# 基本信息
# 视频存放路径
VIDEO_ROOT = config_loader.file("./input/video")

TITLE_PROMPT_FILE = config_loader.file("./input/title_prompt.txt")
CONTENT_PROMPT_FILE = config_loader.file("./input/content_prompt.txt")

TITLE_PIC_FILE = config_loader.file("./input/title.png")

class VideoGenerator(Generator):

  def __init__(self):
    super().__init__(GenerateType.Video)

  def _generate_media(self) -> list:
    files = os.listdir(VIDEO_ROOT)
    file = files[(self.generating_count - 1) % len(files)]
    return [os.path.join(VIDEO_ROOT, file)]
