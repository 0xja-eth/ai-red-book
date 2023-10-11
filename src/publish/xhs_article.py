import time

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from src.core.generator import GenerateType, Generation
from src.core.platform import Platform
from src.core.publisher import Publisher

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

    def _do_login(self) -> list:
        # 扫码登录
        login_ui_path = '//*[@id="page"]/div/div[2]/div[1]/div[2]/div/div/div/div/img'
        self.wait.until(EC.element_to_be_clickable((By.XPATH, login_ui_path)))
        elem = self.driver.find_element(By.XPATH, login_ui_path)
        elem.click()

        # 确定为已登陆状态
        # 等待按钮找到
        self.wait.until(EC.element_to_be_clickable((By.XPATH, ELEMENT['publish'])))
        time.sleep(3)

        # 获取Cookies并返回
        return self.driver.get_cookies()

    def _do_auto_login(self, cookies: list):
        # 将cookies添加到driver中
        for cookie in cookies:
            self.driver.add_cookie(cookie)
        self.driver.refresh()
        self.wait.until(EC.presence_of_element_located((By.XPATH, ELEMENT['username'])))
        time.sleep(3)
        self._save_cookies(self.driver.get_cookies())

    def _get_user_name(self) -> str:
        # 获取用户名
        try:
            uid_element = self.wait.until(EC.presence_of_element_located((By.XPATH, ELEMENT['username'])))
            return uid_element.text
        except NoSuchElementException:
            return ""

    def _get_user_stat(self) -> dict:
        # 获取用户统计数据
        user_dict = {}

        try:
            # 获取关注数
            following_count_element = self.driver.find_element(By.XPATH, ELEMENT['followingCount'])
            following_count = int(following_count_element.text)
            user_dict['followingCount'] = following_count
        except (NoSuchElementException, ValueError):
            user_dict['followingCount'] = 0

        try:
            # 获取粉丝数
            follower_count_element = self.driver.find_element(By.XPATH, ELEMENT['followerCount'])
            follower_count = int(follower_count_element.text)
            user_dict['followerCount'] = follower_count
        except (NoSuchElementException, ValueError):
            user_dict['followerCount'] = 0

        try:
            # 获赞与收藏
            like_and_collect_element = self.driver.find_element(By.XPATH, ELEMENT['likeAndCollectCount'])
            like_and_collect = int(like_and_collect_element.text)
            user_dict['likeCount'] = like_and_collect
            user_dict['collectCount'] = like_and_collect
        except (NoSuchElementException, ValueError):
            user_dict['likeCount'] = 0
            user_dict['collectCount'] = 0

        try:
            # 近七日访客
            recent_visit_element = self.driver.find_element(By.XPATH, ELEMENT['recentVisitCount'])
            recent_visit = int(recent_visit_element.text)
            user_dict['visitCount'] = recent_visit
        except (NoSuchElementException, ValueError):
            user_dict['visitCount'] = 0

        return user_dict

    def _do_publish(self, output: Generation) -> str:
        # 确定为已登陆状态
        # 首先先找到发布笔记，然后点击
        publish_path = '//*[@id="content-area"]/main/div[1]/div/div[1]/a'
        # 等待按钮找到
        self.wait.until(EC.element_to_be_clickable((By.XPATH, publish_path)))
        publish = self.driver.find_element(By.XPATH, publish_path)
        publish.click()
        time.sleep(3)

        upload_i_path0 = '//*[@id="publisher-dom"]/div/div[1]/div/div[1]/div[1]/div[2]'
        self.wait.until(EC.element_to_be_clickable((By.XPATH, upload_i_path0)))
        upload_i = self.driver.find_element(By.XPATH, upload_i_path0)
        upload_i.click()
        time.sleep(3)

        # 输入按钮
        upload_all = self.driver.find_element(By.CLASS_NAME, "upload-input")

        pics = [self._get_abs_path(url) for url in output.urls]
        for pic in pics: upload_all.send_keys(pic)

        # upload_all.send_keys(base_photo1)
        # 判断图片上传成功
        while True:
            time.sleep(2)
            try:
                uploading = 'mask.uploading'
                self.driver.find_element(By.CLASS_NAME, uploading)
                print("Picture is still uploading...")
            except Exception as e:
                break

        print("Picture uploaded!")

        title_text, content_text = output.title, output.content

        content_tags = self._extract_content_tags(self._n2br(content_text))

        JS_CODE_ADD_TEXT = """
      console.log("arguments", arguments)
      var elm = arguments[0], txt = arguments[1], key = arguments[2] || "value";
      elm[key] += txt;
      elm.dispatchEvent(new Event('change'));
    """

        # 填写标题
        title_path = '//*[@id="publisher-dom"]/div/div[1]/div/div[2]/div[2]/div[2]/input'
        title_elm = self.driver.find_element(By.XPATH, title_path)
        self.driver.execute_script(JS_CODE_ADD_TEXT, title_elm, title_text)
        time.sleep(3)

        for content_tag in content_tags:
            content_path = '//*[@id="post-textarea"]'
            content_elm = self.driver.find_element(By.XPATH, content_path)

            if content_tag.startswith("#"):
                topic_path = 'topicBtn'
                topic_elm = self.driver.find_element(By.ID, topic_path)
                topic_elm.click()

                content_tag = content_tag[1:]
                content_elm.send_keys(content_tag)
                time.sleep(3)
                content_elm.send_keys(Keys.ENTER)

            else:
                # 填写内容信息
                self.driver.execute_script(JS_CODE_ADD_TEXT, content_elm, content_tag, "innerHTML")

        time.sleep(3)

        # 发布内容
        p_path = '//*[@id="publisher-dom"]/div/div[1]/div/div[2]/div[2]/div[7]/button[1]'
        p = self.driver.find_element(By.XPATH, p_path)
        p.click()

        # TODO: [莫倪] 获取发布后的URL并返回
        return ""


publisher = XHSArticlePublisher()

# if __name__ == '__main__':
#     publisher.login()
#     print(publisher._get_user_stat())
#     # publisher.multi_publish()
