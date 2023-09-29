
from src.core.generator import GenerateType
from src.generate.article_generate import ArticleGenerator
from src.generate.video_generate import VideoGenerator

GENERATORS = {
  [GenerateType.Article]: ArticleGenerator(),
  [GenerateType.Video]: VideoGenerator()
}