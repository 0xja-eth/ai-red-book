import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from src.core.generator import Generation, GenerateType
from src.core.publisher import Publisher, Platform

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
# def login():
#     driver.get("https://creator.xiaohongshu.com/publish/publish?source=official")
#     # 登录之后采用如下代码输出cookie
#     # for cookie in manual_cookies:
#     #     print(cookie)
#     #     driver.add_cookie(cookie)
#     # driver.get("https://creator.xiaohongshu.com/publish/publish?source=official")
#     # upload_img = driver.find_element(By.XPATH, "//*input[@type='file' and @class=‘upload-input’]")
#
#     # time.sleep(60)
#
#     # 扫码登录
#     login_ui_path = '//*[@id="page"]/div/div[2]/div[1]/div[2]/div/div/div/div/img'
#     element = wait.until(EC.element_to_be_clickable((By.XPATH, login_ui_path)))
#     elem = driver.find_element(By.XPATH, login_ui_path)
#     elem.click()
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
#     # 首先找到发布笔记，然后点击
#     publish_path = '//*[@id="content-area"]/main/div[1]/div/div[1]/a'
#     # 等待按钮找到
#     publish_wait = wait.until(EC.element_to_be_clickable((By.XPATH, publish_path)))
#     publish = driver.find_element(By.XPATH, publish_path)
#     publish.click()
#     time.sleep(3)
#
#     upload_video = driver.find_element(By.CLASS_NAME, "upload-input")
#
#     upload_video.send_keys(pb.get_vi_abspath(count))
#
#     # 等待视频上传完成
#     while True:
#         time.sleep(3)
#         try:
#             driver.find_element(By.CLASS_NAME, "reUpload")
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
#     # 上传标题
#     title_path = "c-input_inner"
#     title_elm = driver.find_element(By.CLASS_NAME, title_path)
#     driver.execute_script(JS_CODE_ADD_TEXT, title_elm, title_text)
#     time.sleep(3)
#
#     # 上传内容
#     content_path = "post-content"
#     content_elm = driver.find_element(By.CLASS_NAME, content_path)
#     driver.execute_script(JS_CODE_ADD_TEXT, content_elm,
#                           content_text.replace("\n", "<br/>"), "innerHTML")
#     time.sleep(3)
#
#     # 上传
#     # css-k3hpu2.css-osq2ks.dyn.publishBtn.red
#     p_path = 'css-k3hpu2.css-osq2ks.dyn.publishBtn.red'
#
#     p_wait = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, p_path)))
#     p = driver.find_element(By.CLASS_NAME, p_path)
#     p.click()
#
#     pb.set_count('count', count)
#
#     print("End publish: %s: %s" % (title_text, content_text))
#
#
# def main():
#     init_driver()
#     #login()
#     AutoLogin(driver, wait, "xhs_video")
#     pb.get_count()
#
#     while True:
#         try:
#             publish()
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

LOGIN_URL = "https://creator.xiaohongshu.com/publish/publish?source=official"


class XHSVideoPublisher(Publisher):

    def __init__(self):
        super().__init__(Platform.XHS, GenerateType.Video, LOGIN_URL)

    def _do_login(self) -> list:
        # 扫码登录
        login_ui_path = '//*[@id="page"]/div/div[2]/div[1]/div[2]/div/div/div/div/img'
        self.wait.until(EC.element_to_be_clickable((By.XPATH, login_ui_path)))
        elem = self.driver.find_element(By.XPATH, login_ui_path)
        elem.click()

        # TODO: [莫倪] 获取Cookies并返回
        return []

    def _get_user_name(self) -> str:
        # TODO: [莫倪] 获取用户名
        pass

    def _get_user_stat(self) -> dict:
        # TODO: [莫倪] 获取用户统计数据
        pass

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
        self.driver.execute_script(JS_CODE_ADD_TEXT, content_elm,
                                   content_text.replace("\n", "<br/>"), "innerHTML")
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

if __name__ == '__main__':
    publisher.multi_publish()
