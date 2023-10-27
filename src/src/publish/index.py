
from src.core.generator import GenerateType
from src.core.platform import Platform

from src.publish import xhs_video, xhs_article, dy_video, wx_video

PUBLISHERS = {
  ("%s_%s" % (Platform.XHS.value, GenerateType.Article.value)): xhs_article.publisher,
  ("%s_%s" % (Platform.XHS.value, GenerateType.Video.value)): xhs_video.publisher,
  ("%s_%s" % (Platform.DY.value, GenerateType.Video.value)): dy_video.publisher,
  ("%s_%s" % (Platform.WX.value, GenerateType.Video.value)): wx_video.publisher,
}

# TODO: 在这里补充所有的Publisher