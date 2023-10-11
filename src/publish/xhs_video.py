import time

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from src.core.generator import Generation, GenerateType
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


class XHSVideoPublisher(Publisher):

    def __init__(self):
        super().__init__(Platform.XHS, GenerateType.Video, LOGIN_URL)

    def _do_login(self) -> list:
        # 扫码登录
        login_ui_path = '//*[@id="page"]/div/div[2]/div[1]/div[2]/div/div/div/div/img'
        self.wait.until(EC.element_to_be_clickable((By.XPATH, login_ui_path)))
        elem = self.driver.find_element(By.XPATH, login_ui_path)
        elem.click()
        # 确定为已登陆状态
        self.wait.until(EC.presence_of_element_located((By.XPATH, ELEMENT['publish'])))
        time.sleep(3)
        # 获取Cookies并返回
        return self.driver.get_cookies()

    def _do_auto_login(self, cookies: list):
        # 将cookies添加到driver中
        for cookie in cookies:
            self.driver.add_cookie(cookie)
        self.driver.refresh()
        self.wait.until(EC.presence_of_element_located((By.XPATH, ELEMENT['publish'])))
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
        # 确定为已登录状态
        # 首先找到发布笔记，然后点击
        publish_path = '//*[@id="content-area"]/main/div[1]/div/div[1]/a'
        # 等待按钮找到
        self.wait.until(EC.element_to_be_clickable((By.XPATH, publish_path)))
        publish = self.driver.find_element(By.XPATH, publish_path)
        publish.click()
        time.sleep(3)

        upload_video = self.driver.find_element(By.CLASS_NAME, "upload-input")
        video_url = self._get_abs_path(output.urls[0])
        upload_video.send_keys(video_url)

        # 等待视频上传完成
        while True:
            time.sleep(3)
            try:
                self.driver.find_element(By.CLASS_NAME, "reUpload")
                break
            except Exception as e:
                print("Video is still uploading...")

        print("Video uploaded!")

        title_text, content_text = output.title, output.content

        JS_CODE_ADD_TEXT = """
          console.log("arguments", arguments)
          var elm = arguments[0], txt = arguments[1], key = arguments[2] || "value";
          elm[key] += txt;
          elm.dispatchEvent(new Event('change'));
      """

        # 上传标题
        title_path = "c-input_inner"
        title_elm = self.driver.find_element(By.CLASS_NAME, title_path)
        self.driver.execute_script(JS_CODE_ADD_TEXT, title_elm, title_text)
        time.sleep(3)

        # 上传内容
        content_path = "post-content"
        content_elm = self.driver.find_element(By.CLASS_NAME, content_path)
        self.driver.execute_script(JS_CODE_ADD_TEXT, content_elm, self._n2br(content_text), "innerHTML")
        time.sleep(3)

        # 上传
        # css-k3hpu2.css-osq2ks.dyn.publishBtn.red
        p_path = 'css-k3hpu2.css-osq2ks.dyn.publishBtn.red'

        self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, p_path)))
        p = self.driver.find_element(By.CLASS_NAME, p_path)
        p.click()
        # TODO: [莫倪] 获取发布后的URL并返回
        return ""


publisher = XHSVideoPublisher()

# if __name__ == '__main__':
#     publisher.login()
#     print(publisher._get_user_stat())
