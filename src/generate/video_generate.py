import os

from src.core.generator import Generator, GenerateType, INPUT_ROOT

# 基本信息
# 视频存放路径
VIDEO_ROOT = os.path.join(INPUT_ROOT, "video")


class VideoGenerator(Generator):

    def __init__(self):
        super().__init__(GenerateType.Video)

    def _generate_media(self) -> list:
        files = os.listdir(VIDEO_ROOT)
        file = files[(self.generating_count - 1) % len(files)]
        return [os.path.join(VIDEO_ROOT, file)]


generator = VideoGenerator()

if __name__ == '__main__':
    generator.multi_generate()
