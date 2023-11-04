import os
import time
import asyncio

import pyppeteer
from pyppeteer import launch

from src.core.generator import Generation, GenerateType
from src.core.publisher import Publisher, Platform, start_parm

LOGIN_URL = "https://creator.xiaohongshu.com/login"

ELEMENT = {
    'publish': '//*[@id="content-area"]/main/div[1]/div/div[1]/a',
    'username': '//*[@id="app"]/div/div[1]/div[1]/div[2]/h4',
    'followingCount': '//*[@id="app"]/div/div[1]/div[1]/div[2]/p[1]/span[1]/label',
    'followerCount': '//*[@id="app"]/div/div[1]/div[1]/div[2]/p[1]/span[2]/label',
    'likeAndCollectCount': '//*[@id="app"]/div/div[1]/div[1]/div[2]/p[1]/span[3]/label',
    'recentVisitCount': '//*[@id="app"]/div/div[1]/div[2]/div[2]/div[3]/span[2]',
}

class XHSArticlePublisher(Publisher):
    def __init__(self):
        super().__init__(Platform.XHS, GenerateType.Article, LOGIN_URL)

    def _get_article_abs_path(self, file_name):
        return os.path.abspath(file_name)

    async def _do_login(self) -> list:
        # 打开网页
        browser = await launch(**start_parm)
        self.page = await browser.newPage()
        await self.page.goto(LOGIN_URL)
        await self.page.waitFor(3000)  # 实测没有等待会报错，不知道原因

        # 进行点击二维码进行登录
        await self.page.click(
            '#page > div > div.content > div.con > div.login-box-container > div > div > div > div > img')
        await self.page.waitForSelector(
            '#content-area > main > div.menu-container.menu-panel > div > div.publish-video > a')  # 等待进入下一个界面

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

    def _get_user_name(self) -> str:
        # # 获取用户名
        # try:
        #     uid_element = self.wait.until(EC.presence_of_element_located((By.XPATH, ELEMENT['username'])))
        #     return uid_element.text
        # except NoSuchElementException:
        #     return ""
        pass

    def _get_user_stat(self) -> dict:
        # # 获取用户统计数据
        # user_dict = {}
        #
        # try:
        #     # 获取关注数
        #     following_count_element = self.driver.find_element(By.XPATH, ELEMENT['followingCount'])
        #     following_count = int(following_count_element.text)
        #     user_dict['followingCount'] = following_count
        # except (NoSuchElementException, ValueError):
        #     user_dict['followingCount'] = 0
        #
        # try:
        #     # 获取粉丝数
        #     follower_count_element = self.driver.find_element(By.XPATH, ELEMENT['followerCount'])
        #     follower_count = int(follower_count_element.text)
        #     user_dict['followerCount'] = follower_count
        # except (NoSuchElementException, ValueError):
        #     user_dict['followerCount'] = 0
        #
        # try:
        #     # 获赞与收藏
        #     like_and_collect_element = self.driver.find_element(By.XPATH, ELEMENT['likeAndCollectCount'])
        #     like_and_collect = int(like_and_collect_element.text)
        #     user_dict['likeCount'] = like_and_collect
        #     user_dict['collectCount'] = like_and_collect
        # except (NoSuchElementException, ValueError):
        #     user_dict['likeCount'] = 0
        #     user_dict['collectCount'] = 0
        #
        # try:
        #     # 近七日访客
        #     recent_visit_element = self.driver.find_element(By.XPATH, ELEMENT['recentVisitCount'])
        #     recent_visit = int(recent_visit_element.text)
        #     user_dict['visitCount'] = recent_visit
        # except (NoSuchElementException, ValueError):
        #     user_dict['visitCount'] = 0
        #
        # return user_dict
        pass

    async def _do_publish(self, output: Generation) -> str:
        # 确定为已登陆状态
        # 首先先找到发布笔记，然后点击
        publish_path = '//*[@id="content-area"]/main/div[1]/div/div[1]/a'
        publish = await self.page.waitForXPath(publish_path)
        # 等待按钮找到
        await publish.click()
        await self.page.waitFor(3000)

        upload_i_path0 = '//*[@id="publisher-dom"]/div/div[1]/div/div[1]/div[1]/div[2]'
        upload_i = await self.page.waitForXPath(upload_i_path0)
        await upload_i.click()
        await self.page.waitFor(3000)

        # upload_article = await self.page.waitForSelector('#web > div > div.upload-container > div.header > div.tab.active')
        # await upload_article.click()

        # 输入按钮
        upload_all = await self.page.querySelector('input[type="file"]')

        # pics = [self._get_article_abs_path(url) for url in output.urls]
        pics = [self._get_abs_path(url) for url in output.urls]
        for pic in pics: await upload_all.uploadFile(pic)

        # upload_all.send_keys(base_photo1)
        # 判断图片上传成功
        # while True:
        #     time.sleep(2)
        #     try:
        #         uploading = 'mask.uploading'
        #         self.driver.find_element(By.CLASS_NAME, uploading)
        #         print("Picture is still uploading...")
        #     except Exception as e:
        #         break
        #
        # print("Picture uploaded!")

        title_text, content_text = output.title, output.content

        # content_tags = self._extract_content_tags(self._n2br(content_text))
        content_tags = self._extract_content_tags(content_text)

        JS_CODE_ADD_TEXT = """
          console.log("arguments", arguments)
          var elm = arguments[0], txt = arguments[1], key = arguments[2] || "value";
          elm[key] += txt;
          elm.dispatchEvent(new Event('change'));
        """

        # 填写标题
        title_path = '//*[@id="publisher-dom"]/div/div[1]/div/div[2]/div[2]/div[2]/input'
        title_elm = await self.page.waitForXPath(title_path)
        await title_elm.type(title_text)
        # self.driver.execute_script(JS_CODE_ADD_TEXT, title_elm, title_text)

        for content_tag in content_tags:
            content_path = '//*[@id="post-textarea"]'
            content_elm = await self.page.waitForXPath(content_path)

            if content_tag.startswith("#"):
                topic_path = '//*[@id="topicBtn"]'
                topic_elm = await self.page.waitForXPath(topic_path)
                await topic_elm.click()

                content_tag = content_tag[1:]
                await content_elm.type(content_tag)
                await self.page.waitFor(3000)
                await content_elm.type('\n')

            else:
                # 填写内容信息
                # self.driver.execute_script(JS_CODE_ADD_TEXT, content_elm, content_tag, "innerHTML")
                await content_elm.type(content_tag)

        await self.page.waitFor(3000)

        # 发布内容
        p_path = '//*[@id="publisher-dom"]/div/div[1]/div/div[2]/div[2]/div[7]/button[1]'
        p = await self.page.waitForXPath(p_path)
        await p.click()

        # TODO: [莫倪] 获取发布后的URL并返回
        return ""


publisher = XHSArticlePublisher()

async def main():
    await publisher.login()
    await publisher.multi_publish()

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())