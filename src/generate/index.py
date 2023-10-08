
from src.core.generator import GenerateType
from src.generate import article_generate
from src.generate import video_generate

GENERATORS = {
  'article': article_generate.generator,
  'video': video_generate.generator
}