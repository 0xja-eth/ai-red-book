
from src.core.generator import GenerateType
from src.generate import article_generate
from src.generate import video_generate

GENERATORS = {
  [GenerateType.Article]: article_generate.generator,
  [GenerateType.Video]: video_generate.generator
}