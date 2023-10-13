import time

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from src.core.generator import GenerateType, Generation
from src.core.platform import Platform
from src.core.publisher import Publisher

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

    def _do_login(self) -> list:
        # 扫码登录
        login_ui_path = '/html/body/div[1]/div/section/header/div[1]/div/div/div/div[2]/span'
        self.wait.until(EC.element_to_be_clickable((By.XPATH, login_ui_path)))
        elem = self.driver.find_element(By.XPATH, login_ui_path)
        elem.click()

        # 确定为已登录状态
        # 等待按钮找到
        self.wait.until(EC.element_to_be_clickable((By.XPATH, ELEMENT['publish'])))
        time.sleep(3)

        # 返回cookies
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
        user_dict = {}
        try:
            # 获取关注数量
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
            # 获取获赞数
            like_count_element = self.driver.find_element(By.XPATH, ELEMENT['likeCount'])
            like_count = int(like_count_element.text)
            user_dict['likeCount'] = like_count
        except (NoSuchElementException, ValueError):
            user_dict['likeCount'] = 0

        try:
            # 获取分享数
            collect_count_element = self.driver.find_element(By.XPATH, ELEMENT['collectCount'])
            collect_count = int(collect_count_element.text)
            user_dict['collectCount'] = collect_count
        except (NoSuchElementException, ValueError):
            user_dict['collectCount'] = 0

        try:
            # 获取播放量
            visit_count_element = self.driver.find_element(By.XPATH, ELEMENT['visitCount'])
            visit_count = int(visit_count_element.text)
            user_dict['visitCount'] = visit_count
        except (NoSuchElementException, ValueError):
            user_dict['visitCount'] = 0

        return user_dict

    def _do_publish(self, output: Generation) -> str:
        # 确定为已登录状态
        # 首先找到发布笔记，然后点击
        publish_path = '//*[@id="root"]/div/div[2]/div[2]/div/div/div/div[1]/button'
        # 等待按钮找到
        self.wait.until(EC.element_to_be_clickable((By.XPATH, publish_path)))
        publish = self.driver.find_element(By.XPATH, publish_path)
        publish.click()

        time.sleep(3)

        # 找到抖音上传视频的按钮
        #upload_video_path = '//*[@id="root"]/div/div/div[3]/div/div[1]/div/div[1]/div/label'
        upload_video_path = '//*[@id="root"]/div/div/div[3]/div/div[1]/div/div[1]/div/label/input'
        upload_video = self.driver.find_element(By.XPATH, upload_video_path)
        video_url = self._get_abs_path(output.urls[0])
        upload_video.send_keys(video_url)

        # 等待视频上传完成
        while True:
            time.sleep(3)
            try:
                reUpload_button_path = '//*[@id="root"]/div/div/div[2]/div[2]/div/div/div[2]/div[4]'
                self.driver.find_element(By.XPATH, reUpload_button_path)
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

        # # 抖音似乎没有上传标题
        # title_path = "c-input_inner"
        # title_elm = self.driver.find_element(By.CLASS_NAME, title_path)
        # self.driver.execute_script(JS_CODE_ADD_TEXT, title_elm, title_text)
        # time.sleep(3)

        # 上传描述内容
        content_path = '//*[@id="root"]/div/div/div[2]/div[1]/div[2]/div/div/div/div[1]/div'
        content_elm = self.driver.find_element(By.XPATH, content_path)
        self.driver.execute_script(JS_CODE_ADD_TEXT, content_elm,
                                   content_text.replace("\n", "<br/>"), "innerHTML")
        time.sleep(3)

        # 发布
        p_path = '//*[@id="root"]/div/div/div[2]/div[1]/div[18]/button[1]'

        self.wait.until(EC.element_to_be_clickable((By.XPATH, p_path)))
        p = self.driver.find_element(By.XPATH, p_path)
        p.click()

        # 获取发布后的URL并返回
        return ""


publisher = DYVideoPublisher()

if __name__ == '__main__':
    publisher.login()
    print(publisher._get_user_stat())
    publisher.multi_publish()
