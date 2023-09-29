import json
import re
import time
from abc import abstractmethod

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from enum import Enum
from dataclasses import dataclass
from dataclasses_json import dataclass_json

import shutil
import os

from src.config import config_loader
from src.config.config_loader import get
from src.core.generator import GenerateType, OUTPUT_ROOT, Generator, Generation
from src.core.state_manager import initial_state, get_state, set_state
from src.generate.index import GENERATORS
from src.utils import api_utils

CHROME_DRIVER_PATH = config_loader.file("./chromedriver.exe")
COOKIES_DIR = config_loader.file("./cookies/")

class Platform(Enum):
  XHS = "xhs"
  DY = "dy"
  WX = "wx"

@dataclass_json
@dataclass
class User:
  id: str
  name: str
  platform: Platform
  cookies: list

  followingCount: int
  followerCount: int
  likeCount: int
  collectCount: int
  visitCount: int

  # def __init__(self, name: str, platform: Platform, cookies: list, stat: dict):
  #   self.name = name
  #   self.platform = platform
  #   self.cookies = cookies
  #
  #   for key in stat: self[key] = stat[key]

  def stat(self):
    return {
      "followingCount": self.followingCount,
      "followerCount": self.followerCount,
      "likeCount": self.likeCount,
      "collectCount": self.collectCount,
      "visitCount": self.visitCount
    }

@dataclass_json
@dataclass
class Publication:
  id: str
  platform: Platform
  userId: str
  generationId: str
  title: str
  content: str
  url: str

  visitCount: int
  likeCount: int
  commentCount: int

class Publisher:

  driver: webdriver.Chrome
  wait: WebDriverWait

  platform: Platform
  generate_type: GenerateType

  login_url: str

  user: User

  def __init__(self, platform, generate_type, login_url):
    self.platform = platform
    self.generate_type = generate_type
    self.login_url = login_url

    if "publish" not in initial_state: initial_state["publish"] = {}
    initial_state["publish"][self.name()] = 0

  def generator(self) -> Generator:
    return GENERATORS[self.generate_type.value]

  def gen_name(self): return self.generator().name()
  def name(self): return "%s_%s" % (self.platform.value, self.gen_name())

  # region Config

  def section_name(self): return "Publish %s %s" % (self.platform.name, self.generate_type.name)

  def load_config(self, key, type): return get(self.section_name(), key, type)

  def interval(self): return self.load_config("interval", "int")
  def is_looped(self): return self.load_config("is_looped", "bool")

  # endregion

  # region State

  def gen_count(self): return get_state("generate", self.gen_name())
  def pub_count(self): return get_state("publish", self.name())
  def add_count(self):
    set_state((self.pub_count() % self.gen_count()) + 1, "publish", self.name())

  # endregion

  # region Cookies

  def cookies_filename(self):
    return os.path.join(COOKIES_DIR, "%s_cookies.json" % self.name())

  def has_cookies(self):
    return os.path.exists(self.cookies_filename())

  def get_cookies(self):
    if not self.has_cookies(): return []
    with open(self.cookies_filename(), "r", encoding="utf8") as file:
      return json.load(file)

  def _save_cookies(self, cookies: list):
    with open(self.cookies_filename(), "w", encoding="utf8") as file:
      json.dump(cookies, file)

  # endregion

  # region Driver

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

  # endregion

  # region Login

  def login(self):
    self.driver.get(self.login_url)

    cookies = self.get_cookies()
    if len(cookies) > 0: self._auto_login(cookies)
    else: cookies = self._do_login()

    self._make_user()
    self._record_login()

  def _auto_login(self, cookies: list):
    # TODO: 自动登陆
    pass

  @abstractmethod
  def _do_login(self) -> list: pass

  def _make_user(self):
    self.user = User(name=self._get_user_name(), platform=self.platform,
                     cookies=self.get_cookies(), **self._get_user_stat())

  @abstractmethod
  def _get_user_name(self) -> str: pass
  @abstractmethod
  def _get_user_stat(self) -> dict: pass

  def _record_login(self):
    login_es = api_utils.login(self.user.name, self.user.platform,
                               self.user.cookies, self.user.stat())
    self.user = User(**login_es["user"])

  # endregion

  # region Publish

  def publish(self):
    if self.pub_count() >= self.gen_count() and not self.is_looped(): return True

    print("Start publish %s: %d/%d" % (self.name(), self.pub_count() + 1, self.gen_count()))

    generate_id = self.generator().generation_ids()[self.pub_count()]
    output = self.generator().get_output(generate_id)
    if output is None: return False

    url = self._do_publish(output)

    publication = self._upload_publication(output, url)

    self.add_count()

    print("End publish %s: %d/%d -> %s" % (
      self.name(), self.pub_count(), self.gen_count(), publication
    ))

  @abstractmethod
  def _do_publish(self, output: Generation) -> str: pass

  def _upload_publication(self, output: Generation, url: str) -> Publication:
    # TODO: 构建并上传Publication
    pass

  def multi_publish(self):
    while True:
      try:
        flag = self.publish()
        if flag: break
        if flag is None: time.sleep(self.interval())
      except Exception as e:
        print("Error publish: %s" % str(e))

      self.driver.refresh()

  # endregion

  # region Utils

  @staticmethod
  def _get_abs_path(file_name):
    return os.path.abspath(os.path.join(OUTPUT_ROOT, file_name))

  @staticmethod
  def _br_ize(text):
    return text.replace("\n", "<br/>")

  @staticmethod
  def _extract_content_tags(text):
    segments = re.split(r'#\w+', text)
    hashtags = re.findall(r'#\w+', text)
    result = []

    for i in range(max(len(segments), len(hashtags))):
      if i < len(segments) and segments[i].strip() != '':
        result.append(segments[i].strip())
      if i < len(hashtags):
        result.append(hashtags[i])

    return result

  # endregion