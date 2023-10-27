import json
import re
import time
from abc import abstractmethod

from dataclasses import dataclass

import pyppeteer
from dataclasses_json import dataclass_json
from src.core.platform import Platform

import asyncio
from pyppeteer import launch

from src.config import config_loader
from src.config.config_loader import get
from src.core.generator import GenerateType, OUTPUT_ROOT, Generator, Generation
from src.core.state_manager import initial_state, get_state, set_state
from src.generate.index import GENERATORS
from src.utils import api_utils

import shutil
import os
import configparser

VIDEO_COUNT_FILE = "./vcount.txt"
PUB_VIDEO_COUNT_FILE = "./vpub_count.txt"

COOKIES_DIR = config_loader.file("./cookies/")

OUTPUT_ROOT = "./voutput"

video_path = "./1-vi.mp4"
title_path = "./title_prompt.txt"
content_path = "./content_prompt.txt"

start_parm = {
    # 关闭无头浏览器 默认是无头启动的
    "headless": False
}


@dataclass_json
@dataclass
class User:
    id: str
    name: str
    platform: Platform
    cookies: list

    state: str

    createdAt: str
    updatedAt: str

    followingCount: int = 0
    followerCount: int = 0
    likeCount: int = 0
    collectCount: int = 0
    visitCount: int = 0

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

    state: str

    createdAt: str
    updatedAt: str

    visitCount: int = 0
    likeCount: int = 0
    commentCount: int = 0

    visitCount: int = 0
    likeCount: int = 0
    commentCount: int = 0


class Publisher:
    platform: Platform
    generate_type: GenerateType

    login_url: str
    user: User

    page: pyppeteer.page
    loop = asyncio.new_event_loop()

    def __init__(self, platform: Platform, generate_type: GenerateType, login_url: str):
        self.platform = platform
        self.generate_type = generate_type
        self.login_url = login_url
        self.user = None
        self.page = None

        if "publish" not in initial_state: initial_state["publish"] = {}
        initial_state["publish"][self.name()] = 0

    def generator(self) -> Generator:
        return GENERATORS[self.generate_type.value]

    def gen_name(self):
        return self.generator().name()

    def name(self):
        return "%s_%s" % (self.platform.value, self.gen_name())

    # region Config

    def section_name(self):
        return "Publish %s %s" % (self.platform.name, self.generate_type.name)

    def load_config(self, key, type):
        return get(self.section_name(), key, type)

    def interval(self):
        return self.load_config("interval", "int")

    def is_looped(self):
        return self.load_config("is_looped", "bool")

    # endregion

    # region State

    def gen_count(self):
        return self.generator().gen_count()

    def pub_count(self):
        return get_state("publish", self.name(), default=0)

    def _add_count(self):
        set_state((self.pub_count() + 1) % self.gen_count(), "publish", self.name())

    def _clear_count(self):
        set_state(0, "publish", self.name())

    # endregion

    # region Cookies

    def cookies_filename(self):
        # 是否存在cookies文件夹，不存在则创建
        if not os.path.exists(COOKIES_DIR):
            os.makedirs(COOKIES_DIR)
        return os.path.join(COOKIES_DIR, "%s_cookies.json" % self.name())

    def has_cookies(self):
        return os.path.exists(self.cookies_filename())

    def get_cookies(self):
        if not self.has_cookies(): return []
        with open(self.cookies_filename(), "r", encoding="utf8") as file:
            return json.load(file)

    def _save_cookies(self, cookies: list):
        with open(self.cookies_filename(), "w", encoding="utf8") as file:
            file.truncate()
        with open(self.cookies_filename(), "w", encoding="utf8") as file:
            json.dump(cookies, file)

    # endregion

    # region resize
    def screen_size(self):
        # 使用tkinter获取屏幕大小
        import tkinter
        tk = tkinter.Tk()
        width = tk.winfo_screenwidth()
        height = tk.winfo_screenheight()
        tk.quit()
        return width, height

    async def screen_resize(self):
        width, height = self.screen_size()
        await self.page.setViewport({
            "width": width,
            "height": height
        })

    # endregion

    # region Login

    async def login(self):
        cookies = self.get_cookies()
        if len(cookies) > 0:
            await self._auto_login(cookies)
        else:
            cookies = await self._do_login()
            if len(cookies) > 0:
                self._save_cookies(cookies)

        # await self.screen_resize()
        raw_user = self._make_raw_user(cookies)
        self._record_login(raw_user)

    async def _auto_login(self, cookies: list):
        # 自动登陆，如果需要子类实现，写一个 _do_auto_login 函数
        # self.loop.run_until_complete(self._do_auto_login(cookies))
        await self._do_auto_login(cookies)

    @abstractmethod
    async def _do_auto_login(self, cookies: list):
        pass

    @abstractmethod
    async def _do_login(self) -> list:
        pass

    def _make_raw_user(self, cookies):
        return {
            "name": self._get_user_name(),
            "platform": self.platform.value,
            "cookies": cookies,
            "stat": self._get_user_stat()
        }

    @abstractmethod
    def _get_user_name(self) -> str:
        pass

    @abstractmethod
    def _get_user_stat(self) -> dict:
        pass

    def _record_login(self, raw_user):
        pass
        # login_res = api_utils.login(**raw_user)
        # self.user = User(**login_res["user"])

    # endregion

    async def publish(self):
        """
            发布一条内容
            :return: True if need to break, False if continue next one, None if all success
            """
        if self.pub_count() >= self.gen_count() and not self.is_looped(): return True

        print("Start publish %s: %d/%d" % (self.name(), self.pub_count() + 1, self.gen_count()))

        generate_id = self.generator().generation_ids()[self.pub_count()]
        output = self.generator().get_output(generate_id)
        if output is None: return False

        url = await self._do_publish(output)

        publication = self._upload_publication(output, url)

        self._add_count()

        print("End publish %s: %d/%d -> %s" % (
            self.name(), self.pub_count(), self.gen_count(), publication
        ))

    @abstractmethod
    async def _do_publish(self, output: Generation) -> str:
        pass

    def _upload_publication(self, output: Generation, url: str) -> Publication:
        return Publication(**api_utils.publish({
            "platform": self.platform.value,
            "userId": self.user.id,
            "generationId": output.id,
            "title": output.title,
            "content": output.content,
            "url": url
        }))

    async def multi_publish(self):
        while True:
            try:
                flag = await self.publish()
                if flag is True: break
                if flag is False: continue
                if flag is None: time.sleep(self.interval())
            except Exception as e:
                print("Error publish: %s" % str(e))

            # self.driver.refresh()

    # endregion

    # region Utils

    @staticmethod
    def _get_abs_path(file_name):
        return os.path.abspath(config_loader.file(file_name))

    @staticmethod
    def _n2br(text):
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

# async def main():
#     # 设置参数，打开浏览器页面
#     browser = await launch(**start_parm)
#     page = await browser.newPage()
#     await page.goto('https://creator.xiaohongshu.com/publish/publish?source=official')
#     await page.waitFor(3000)  # 实测没有等待会报错，不知道原因
#
#     # 进行点击二维码进行登录
#     await page.click('#page > div > div.content > div.con > div.login-box-container > div > div > div > div > img')
#     await page.waitForSelector(
#         '#content-area > main > div.menu-container.menu-panel > div > div.publish-video > a')  # 等待进入下一个界面
#     # 点击‘发布视频’
#     await page.click('#content-area > main > div.menu-container.menu-panel > div > div.publish-video > a')
#     await page.waitForSelector(
#         '#publish-container > div > div.video-uploader-container.upload-area > div.upload-wrapper > div > div > div')
#     # 上传视频
#     upload_video = await page.waitForSelector('input[type="file"]')
#     await upload_video.uploadFile(video_path)
#     # 上传标题和文本
#     upload_title = await page.waitForSelector(
#         '#publish-container > div > div:nth-child(3) > div.content > div.c-input.titleInput > input')
#     await upload_title.type(get_title())
#     upload_content = await page.waitForSelector('#post-textarea')
#     await upload_content.type(get_content())
#
#     # 等待确保发布按钮可以点击，暂时还没找到判断按钮是否可以点击的API
#
#     await page.waitFor(4000)
#     # 点击上传
#     await page.click(
#         '#publish-container > div > div:nth-child(3) > div.content > div.submit > button.css-k3hpu2.css-osq2ks.dyn.publishBtn.red')
#
#     await page.waitFor(5000)
#     await browser.close()
#
#
# # driver: webdriver.Chrome
# # wait: WebDriverWait
#
# # 读取配置文件
# config = configparser.ConfigParser()
# config.read("./config.ini")
#
# with open(VIDEO_COUNT_FILE, encoding="utf8") as vc_file:
#     max_count = int(vc_file.read())
#
# with open(PUB_VIDEO_COUNT_FILE, encoding="utf8") as vc_file:
#     count = int(vc_file.read())
#
#
# def get_title():
#     with open(title_path, encoding="utf8") as file:
#         return file.read()
#
#
# def get_content():
#     with open(content_path, encoding="utf8") as file:
#         return file.read()
#
#
# if __name__ == '__main__':
#     interval = int(config.get('VPublish', 'interval'))
#     is_looped = config.get('VPublish', 'is_looped').lower() == "true"
#     asyncio.new_event_loop().run_until_complete(main())
