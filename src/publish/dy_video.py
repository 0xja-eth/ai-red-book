import time
import asyncio

import pyppeteer
from pyppeteer import launch

from src.core.generator import Generation, GenerateType
from src.core.publisher import Publisher, Platform, start_parm

LOGIN_URL = "https://creator.douyin.com/"

ELEMENT = {
    'publish': '//*[@id="root"]/div/div[2]/div[2]/div/div/div/div[1]/button',
    'username': '//*[@id="root"]/div/div[1]/div/div/div[2]/div[1]/div[1]/div[1]',
    'followingCount': '//*[@id="root"]/div/div[1]/div/div/div[2]/div[2]/div[1]/div[2]/span',
    'followerCount': '//*[@id="root"]/div/div[1]/div/div/div[2]/div[2]/div[1]/div[3]/span',
    'likeCount': '//*[@id="root"]/div/div[1]/div/div/div[2]/div[2]/div[1]/div[1]/span',
    'collectCount': '//*[@id="root"]/div/div[4]/div/div[2]/div[2]/div[1]/div/div/div[6]/div[2]/div[1]',
    'visitCount': '//*[@id="root"]/div/div[4]/div/div[2]/div[2]/div[1]/div/div/div[1]/div[2]/div[1]',
}


class DYVideoPublisher(Publisher):
    def __init__(self):
        super().__init__(Platform.DY, GenerateType.Video, LOGIN_URL)

    async def _do_login(self) -> list:
        # 打开网页
        browser = await launch(**start_parm)
        self.page = await browser.newPage()
        await self.page.goto(LOGIN_URL)
        await self.page.waitFor(3000)  # 实测没有等待会报错，不知道原因
        # 扫码登录
        await self.page.click(
            '#root > div > section > header > div.creator-header-wrapper > div > div > div > div.semi-navigation-footer > span')
        await self.page.waitForSelector(
            '#root > div > div.content--3ncCf.creator-content > div.sider--137Dm > div > div > div > div.semi-navigation-header > button')  # 等待进入下一个界面

        # TODO: [莫倪] 获取Cookies并返回
        return await self.page.cookies()

    async def _do_auto_login(self, cookies: list):
        browser = await launch(**start_parm)
        self.page = await browser.newPage()

        for cookie in cookies:
            await self.page.setCookie(cookie)

        await self.page.goto(self.login_url)
        await self.page.reload()
        await self.page.waitFor(3000)

    async def _do_publish(self, output: Generation) -> str:
        # 确定为已登录状态
        # 首先找到发布笔记，然后点击
        publish_btn_path = '//*[@id="root"]/div/div[2]/div[2]/div/div/div/div[1]/button'
        publish_btn = await self.page.waitForXPath(publish_btn_path)
        await publish_btn.click()
        await publish_btn.click()
        await self.page.waitForSelector(
            '#root > div > div > div.semi-tabs.semi-tabs-top > div > div.semi-tabs-pane-active.semi-tabs-pane > div > div.container--1GAZf > div > label > input')

        # 上传视频
        # upload_video = await self.page.waitForSelector(
        #    '#root > div > div > div.semi-tabs.semi-tabs-top > div > div.semi-tabs-pane-active.semi-tabs-pane > div > div.container--1GAZf > div > label > input')
        upload_video = await self.page.waitForXPath('//*[@id="root"]/div/div/div[3]/div/div[1]/div/div[1]/div/label/input')
        video_url = self._get_abs_path(output.urls[0])
        await upload_video.uploadFile(video_url)
        await self.page.waitFor(2000)

        upload_btn = await self.page.waitForSelector('input[type="file"]')
        await upload_btn.uploadFile(video_url)

        title_text, content_text = output.title, output.content
        # 上传标题和文本
        upload_content = await self.page.waitForSelector(
            '#root > div > div > div.content-body--1ae6Q > div.form--3R0Ka > div.editor-container--1QyLV > div > div > div > div.outerdocbody.editor-kit-outer-container > div')
        await upload_content.type(content_text)

        # 等待确保发布按钮可以点击，暂时还没找到判断按钮是否可以点击的API

        await self.page.waitFor(4000)
        # 点击上传
        await self.page.click(
            '#root > div > div > div.content-body--1ae6Q > div.form--3R0Ka > div.content-confirm-container--anYOC > button.button--1SZwR.primary--1AMXd.fixed--3rEwh')

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


publisher = DYVideoPublisher()


async def main():
    await publisher.login()
    await publisher.multi_publish()


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
