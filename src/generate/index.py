from src.core.generator import GenerateType
from src.generate import article_generate
from src.generate import video_generate

GENERATORS = {
    GenerateType.Article.value: article_generate.generator,
    GenerateType.Video.value: video_generate.generator
}
