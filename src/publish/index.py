
from src.core.generator import GenerateType
from src.core.publisher import Platform
from src.generate.article_generate import ArticleGenerator
from src.generate.video_generate import VideoGenerator

PUBLISHERS = {
  ["%s_%s" % (Platform.XHS, GenerateType.Article)]: ArticleGenerator(),
  ["%s_%s" % (Platform.XHS, GenerateType.Article)]: ArticleGenerator(),
}