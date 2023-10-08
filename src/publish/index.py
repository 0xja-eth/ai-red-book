
from src.core.generator import GenerateType
from src.core.platform import Platform

from src.publish import xhs_video, xhs_article, dy_video, wx_video

PUBLISHERS = {
  ["%s_%s" % (Platform.XHS, GenerateType.Article)]: xhs_article.publisher,
  ["%s_%s" % (Platform.XHS, GenerateType.Video)]: xhs_video.publisher,
}

# TODO: 在这里补充所有的Publisher