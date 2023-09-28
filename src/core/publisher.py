from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from enum import Enum

import shutil
import os

from src.utils import api_utils

CHROME_DRIVER_PATH = "./chromedriver.exe"

class Platform(Enum):
  XHS = "xhs"
  DY = "dy"
  WX = "wx"

class GenerateType(Enum):
  Article = "article"
  Video = "video"

class User:
  name: str
  platform: Platform
  cookies: dict

  followingCount: int
  followerCount: int
  likeCount: int
  collectCount: int
  visitCount: int

  def stat(self):
    return {
      "followingCount": self.followingCount,
      "followerCount": self.followerCount,
      "likeCount": self.likeCount,
      "collectCount": self.collectCount,
      "visitCount": self.visitCount
    }

class Publisher:

  driver: webdriver.Chrome
  wait: WebDriverWait

  platform: Platform
  generate_type: GenerateType

  login_url: str

  user: User

  count: int = 0
  pub_count: int = 0

  def __init__(self, platform, generate_type, login_url):
    self.platform = platform
    self.generate_type = generate_type
    self.login_url = login_url

  def init_driver(self):
    if not os.path.exists(CHROME_DRIVER_PATH):
      self._download_driver()

    chromedriver_path = Service(CHROME_DRIVER_PATH)
    self.driver = webdriver.Chrome(service=chromedriver_path)
    self.wait = WebDriverWait(self.driver, 120)

  def _download_driver(self):
    chromedriver_path = ChromeDriverManager().install()

    # 将chromedriver移动到当前目录
    new_chromedriver_path = CHROME_DRIVER_PATH
    shutil.copy(chromedriver_path, new_chromedriver_path)

  def login(self):
    self.driver.get(self.login_url)
    self._do_login()

    self.user = self._make_user()
    self._record_login()

  def _do_login(self): pass

  def _make_user(self) -> User: pass

  def _record_login(self):
    login_es = api_utils.login(self.user.name, self.user.platform,
                               self.user.cookies, self.user.stat())
    self.user = login_es["user"]

  def publish(self):
    pass
