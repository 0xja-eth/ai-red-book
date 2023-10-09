import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from src.core.generator import GenerateType, Generation
from src.core.platform import Platform
from src.core.publisher import Publisher

#
# driver: webdriver.Chrome
# wait: WebDriverWait
#
#
# # 初始化浏览器驱动
# def init_driver():
#     global driver, wait
#
#     if not os.path.exists("../../chromedriver.exe"):
#         pb.download_driver()
#
#     chromedriver_path = Service("../../chromedriver.exe")
#     driver = webdriver.Chrome(service=chromedriver_path)
#     wait = WebDriverWait(driver, 120)
#
#
# # 发布视频
# def publish():
#     global count
#
#     pb.count = pb.count % pb.max_count + 1
#
#     print("Start publish video: %d / %d" % (pb.count, pb.max_count))
#
#     # 确定为已登录状态
#     # 首先找到发布视频，然后点击
#
#     publish_path = '/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[1]/button/span/span'
#     # 等待按钮找到
#     publish_wait = wait.until(EC.element_to_be_clickable((By.XPATH, publish_path)))
#     publish = driver.find_element(By.XPATH, publish_path)
#     publish.click()
#     time.sleep(3)
#
#     upload_video = driver.find_element(By.CLASS_NAME, "upload-btn-input--1NeEX")
#
#     upload_video.send_keys(pb.get_vi_abspath(count))
#
#     # 等待视频上传完成
#     while True:
#         time.sleep(3)
#         try:
#             driver.find_element(By.CLASS_NAME, "upload-btn--9eZLd")
#             break
#         except Exception as e:
#             print("视频还在上传中···")
#
#     print("视频已上传完成！")
#
#     # 需要再修改
#     title_text = pb.get_title(count)
#     content_text = pb.get_content(count)
#
#     JS_CODE_ADD_TEXT = """
#          console.log("arguments", arguments)
#          var elm = arguments[0], txt = arguments[1], key = arguments[2] || "value";
#          elm[key] += txt;
#          elm.dispatchEvent(new Event('change'));
#        """
#
#     # 上传标题（抖音好像没有标题）
#     # title_path = "c-input_inner"
#     # title_elm = driver.find_element(By.CLASS_NAME, title_path)
#     # driver.execute_script(JS_CODE_ADD_TEXT, title_elm, title_text)
#     # time.sleep(3)
#
#
#     # 上传内容
#     content_tags = pb.extract_content_tags(content_text.replace("\n", "<br/>"))
#
#     content_path = '//*[@id="root"]/div/div/div[2]/div[1]/div[2]/div/div/div/div[1]/div'
#     content_elm = driver.find_element(By.XPATH, content_path)
#     driver.execute_script(JS_CODE_ADD_TEXT, content_elm,
#                           content_text.replace("\n", "<br/>"), "innerHTML")
#     time.sleep(3)
#
#     for content_tag in content_tags:
#         content_path = '//*[@id="root"]/div/div/div[2]/div[1]/div[2]/div/div/div/div[1]/div'
#         content_elm = driver.find_element(By.XPATH, content_path)
#
#         if content_tag.startswith("#"):
#             topic_path = '//*[@id="root"]/div/div/div[2]/div[1]/div[2]/div/div/div[1]/div[2]/div[1]/div/div/div[1]'
#             topic_elm = driver.find_element(By.XPATH, topic_path)
#             topic_elm.click()
#
#             content_tag = content_tag[1:]
#             content_elm.send_keys(content_tag)
#             time.sleep(3)
#             content_elm.send_keys(Keys.ENTER)
#
#         else:
#             # 填写内容信息
#             driver.execute_script(JS_CODE_ADD_TEXT, content_elm, content_tag, "innerHTML")
#             # content.send_keys(description)
#
#     time.sleep(3)
#
#     # 上传
#     p_path = '//*[@id="root"]/div/div/div[2]/div[1]/div[17]/button[1]'
#     p_wait = wait.until(EC.element_to_be_clickable((By.XPATH, p_path)))
#     p = driver.find_element(By.XPATH, p_path)
#     p.click()
#     # driver.find_element_by_xpath('//*[@id="root"]/div/div/div[2]/div[1]/div[17]/button[1]').click()
#
#     pb.set_count('count', count)
#
#     print("End publish: %s: %s" % (title_text, content_text))
#
#
# def main():
#     init_driver()
#     AutoLogin(driver, wait, "dy_video")
#
#     while True:
#         try:
#             publish()
#             print(interval)
#             time.sleep(interval)
#         except Exception as e:
#             print("Error publish: %s" % str(e))
#
#         driver.refresh()
#         if pb.count >= pb.max_count and not is_looped: break
#
#
# if __name__ == '__main__':
#     interval = int(pb.config.get('VPublish', 'interval'))
#     is_looped = pb.config.get('VPublish', 'is_looped').lower() == "true"
#
#     main()

LOGIN_URL = "https://creator.douyin.com/"

ELEMENT = {
    'publish': '//*[@id="root"]/div/div[2]/div[2]/div/div/div/div[1]/button',
    'username': '//*[@id="root"]/div/div[1]/div/div/div[2]/div[1]/div[1]/div[1]',
    'followingCount': '//*[@id="root"]/div/div[1]/div/div/div[2]/div[2]/div[1]/div[2]/span',
    'followerCount': '//*[@id="root"]/div/div[1]/div/div/div[2]/div[2]/div[1]/div[3]/span',
    'likeCount': '//*[@id="root"]/div/div[4]/div/div[2]/div[2]/div[1]/div/div/div[3]/div[2]/div[1]',
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
        # 首先找到发布笔记，然后点击
        publish_path = '//*[@id="root"]/div/div[2]/div[2]/div/div/div/div[1]/button'
        # 等待按钮找到
        self.wait.until(EC.element_to_be_clickable((By.XPATH, publish_path)))

        # 返回cookies
        return self.driver.get_cookies()

    def _do_auto_login(self, cookies: list):
        self.driver.get(LOGIN_URL)
        # 将cookies添加到driver中
        for cookie in cookies:
            self.driver.add_cookie(cookie)
        self.driver.refresh()
        self.wait.until(EC.presence_of_element_located((By.XPATH, ELEMENT['publish'])))
        time.sleep(3)
        self._save_cookies(self.driver.get_cookies())

    def _get_user_name(self) -> str:
        username_element = self.driver.find_element(By.XPATH, ELEMENT['username'])
        return username_element.text

    def _get_user_stat(self) -> dict:
        user_dict = {}
        # 获取关注数量
        followingCount_element = self.driver.find_element(By.XPATH, ELEMENT['followingCount'])
        follwoingCount = int(followingCount_element.text)
        user_dict['followingCount'] = follwoingCount

        # 获取粉丝数
        followerCount_element = self.driver.find_element(By.XPATH, ELEMENT['followerCount'])
        followerCount = int(followerCount_element.text)
        user_dict['followerCount'] = followerCount

        # 获取获赞数
        likeCount_element = self.driver.find_element(By.XPATH, ELEMENT['likeCount'])
        likeCount = int(likeCount_element.text)
        user_dict['likeCount'] = likeCount

        # 获取分享数
        collectCount_element = self.driver.find_element(By.XPATH, ELEMENT['collectCount'])
        collectCount = int(collectCount_element.text)
        user_dict['collectCount'] = collectCount

        # 获取播放量
        visitCount_element = self.driver.find_element(By.XPATH, ELEMENT['visitCount'])
        visitCount = int(visitCount_element.text)
        user_dict['visitCount'] = visitCount
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
    upload_video_path = '//*[@id="root"]/div/div/div[3]/div/div[1]/div/div[1]/div/label'
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
    p_path = '//*[@id="root"]/div/div/div[2]/div[1]/div[17]/button[1]'

    self.wait.until(EC.element_to_be_clickable((By.XPATH, p_path)))
    p = self.driver.find_element(By.XPATH, p_path)
    p.click()

    # 获取发布后的URL并返回
    return ""


# TODO: [丰含] 根据xhs_article, xhs_video的重构方法，重构dy_video

publisher = DYVideoPublisher()

if __name__ == '__main__':
    publisher.login()
    print('username', publisher._get_user_name())
    print(publisher._get_user_stat())
    publisher.driver.quit()
