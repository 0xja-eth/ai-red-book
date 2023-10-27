import time
import asyncio

import pyppeteer
from pyppeteer import launch

from src.core.generator import Generation, GenerateType
from src.core.publisher import Publisher, Platform, START_OPTION

LOGIN_URL = "https://creator.xiaohongshu.com/publish/publish?source=official"

ELEMENT = {
    'publish': '//*[@id="content-area"]/main/div[1]/div/div[1]/a',
    'username': '//*[@id="app"]/div/div[1]/div[1]/div[2]/h4',
    'followingCount': '//*[@id="app"]/div/div[1]/div[1]/div[2]/p[1]/span[1]/label',
    'followerCount': '//*[@id="app"]/div/div[1]/div[1]/div[2]/p[1]/span[2]/label',
    'likeAndCollectCount': '//*[@id="app"]/div/div[1]/div[1]/div[2]/p[1]/span[3]/label',
    'recentVisitCount': '//*[@id="app"]/div/div[1]/div[2]/div[2]/div[3]/span[2]',
}

class XHSVideoPublisher(Publisher):

    def __init__(self):
        super().__init__(Platform.XHS, GenerateType.Video, LOGIN_URL)

    async def _do_login(self):
        # 打开网页
        browser = await launch(**START_OPTION)
        self.page = await browser.newPage()
        await self.page.goto(LOGIN_URL)
        await self.page.waitFor(3000)  # 实测没有等待会报错，不知道原因

        # 进行点击二维码进行登录
        await self.page.click('#page > div > div.content > div.con > div.login-box-container > div > div > div > div > img')
        await self.page.waitForSelector(
            '#content-area > main > div.menu-container.menu-panel > div > div.publish-video > a')  # 等待进入下一个界面

        # TODO: [莫倪] 获取Cookies并返回
        return await self.page.cookies()

    async def _do_auto_login(self, cookies: list):
        browser = await launch(**START_OPTION)
        self.page = await browser.newPage()

        for cookie in cookies:
            await self.page.setCookie(cookie)

        await self.page.goto(self.login_url)
        await self.page.reload()
        await self.page.waitFor(3000)

    def _get_user_name(self) -> str:
        # TODO: [莫倪] 获取用户名
        pass

    def _get_user_stat(self) -> dict:
        # TODO: [莫倪] 获取用户统计数据
        pass

    async def _do_publish(self, output: Generation) -> str:
        # 确定为已登录状态
        # 首先找到发布笔记，然后点击
        await self.page.click('#content-area > main > div.menu-container.menu-panel > div > div.publish-video > a')
        await self.page.waitForSelector(
            '#publish-container > div > div.video-uploader-container.upload-area > div.upload-wrapper > div > div > div')
        # 上传视频
        upload_video = await self.page.querySelector('input[type="file"]')
        video_url = self._get_abs_path(output.urls[0])
        await upload_video.uploadFile(video_url)

        title_text, content_text = output.title, output.content

        #上传标题和文本
        upload_title = await self.page.waitForSelector(
            '#publish-container > div > div:nth-child(3) > div.content > div.c-input.titleInput > input')
        await upload_title.type(title_text)
        upload_content = await self.page.waitForSelector('#post-textarea')
        await upload_content.type(content_text)

        # 等待确保发布按钮可以点击，暂时还没找到判断按钮是否可以点击的API

        await self.page.waitFor(4000)
        # 点击上传
        await self.page.click(
            '#publish-container > div > div:nth-child(3) > div.content > div.submit > button.css-k3hpu2.css-osq2ks.dyn.publishBtn.red')

        await self.page.waitFor(5000)

        # 等待视频上传完成
        # TODO:检测是否上传完成

        # title_text, content_text = output.title, output.content

        JS_CODE_ADD_TEXT = """
         console.log("arguments", arguments)
         var elm = arguments[0], txt = arguments[1], key = arguments[2] || "value";
         elm[key] += txt;
         elm.dispatchEvent(new Event('change'));
        """

        # TODO: [莫倪] 获取发布后的URL并返回
        return ""

publisher = XHSVideoPublisher()

async def main():
    await publisher.login()
    await publisher.multi_publish()

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())