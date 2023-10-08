import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from src.core.generator import GenerateType, Generation
from src.core.publisher import Publisher, Platform

# driver: webdriver.Chrome
# wait: WebDriverWait
#
# # 读取配置文件
#
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
# cookiesFilename="./xhs_article_cookies.json"
# def load_cookies():
#     #检测是否存在cookies文件
#     if not os.path.exists(cookiesFilename):
#         return []
#     #返回cookies
#     with open(cookiesFilename, "r", encoding="utf8") as file:
#         cookies = json.load(file)
#     return cookies
#
# def save_cookies():
#     cookies = driver.get_cookies()
#     print("cookies:", cookies)
#     #清空cookies文件
#     with open(cookiesFilename, "w", encoding="utf8") as file:
#         file.truncate()
#     with open(cookiesFilename, "w", encoding="utf8") as file:
#         json.dump(cookies, file)
#
# def login():
#     driver.get("https://creator.xiaohongshu.com/")
#     cookies = load_cookies()
#     for cookie in cookies:
#         driver.add_cookie(cookie)
#     driver.refresh()
#
#     # 扫码登录
#     login_ui_path = '//*[@id="page"]/div/div[2]/div[1]/div[2]/div/div/div/div/img'
#     element = wait.until(EC.element_to_be_clickable((By.XPATH, login_ui_path)))
#     elem = driver.find_element(By.XPATH, login_ui_path)
#     elem.click()
#
#     # 确保登陆成功后（出现发布按钮）保存cookies：
#     wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='publish-video']")))
#     save_cookies()
#
#
# def publish():
#     global count
#
#     pb.count = pb.count % pb.max_count + 1
#
#     print("Start publish: %d / %d" % (pb.count, pb.max_count))
#
#     # 确定为已登陆状态
#     # 首先先找到发布笔记，然后点击
#     publish_path = '//*[@id="content-area"]/main/div[1]/div/div[1]/a'
#     # 等待按钮找到
#     publish_wait = wait.until(EC.element_to_be_clickable((By.XPATH, publish_path)))
#     publish = driver.find_element(By.XPATH, publish_path)
#     publish.click()
#     time.sleep(3)
#
#     upload_i_path0 = '//*[@id="publisher-dom"]/div/div[1]/div/div[1]/div[1]/div[2]'
#     upload_wait = wait.until(EC.element_to_be_clickable((By.XPATH, upload_i_path0)))
#     upload_i = driver.find_element(By.XPATH, upload_i_path0)
#     upload_i.click()
#     time.sleep(3)
#
#     # 输入按钮
#     upload_all = driver.find_element(By.CLASS_NAME, "upload-input")
#
#     pics = pb.get_pics_abspath(count)
#     # upload_all.send_keys(*pics)
#     for pic in pics: upload_all.send_keys(pic)
#
#     # upload_all.send_keys(base_photo1)
#     # 判断图片上传成功
#     while True:
#         time.sleep(2)
#         try:
#             uploading = 'mask.uploading'
#             driver.find_element(By.CLASS_NAME, uploading)
#             print("图片正在上传中……")
#         except Exception as e:
#             break
#     print("已经上传图片")
#
#     title_text = pb.get_title(count)
#     content_text = pb.get_content(count)
#
#     content_tags = pb.extract_content_tags(content_text.replace("\n", "<br/>"))
#
#     JS_CODE_ADD_TEXT = """
#       console.log("arguments", arguments)
#       var elm = arguments[0], txt = arguments[1], key = arguments[2] || "value";
#       elm[key] += txt;
#       elm.dispatchEvent(new Event('change'));
#     """
#
#     # 填写标题
#     title_path = '//*[@id="publisher-dom"]/div/div[1]/div/div[2]/div[2]/div[2]/input'
#     title_elm = driver.find_element(By.XPATH, title_path)
#     driver.execute_script(JS_CODE_ADD_TEXT, title_elm, title_text)
#     # title.send_keys(title_content)
#     time.sleep(3)
#
#     for content_tag in content_tags:
#         content_path = '//*[@id="post-textarea"]'
#         content_elm = driver.find_element(By.XPATH, content_path)
#
#         if content_tag.startswith("#"):
#             topic_path = 'topicBtn'
#             topic_elm = driver.find_element(By.ID, topic_path)
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
#     # 发布内容
#     p_path = '//*[@id="publisher-dom"]/div/div[1]/div/div[2]/div[2]/div[7]/button[1]'
#     pp_path = '//*[@id="publisher-dom"]/div/div[1]/div/div[2]/div[2]/div[7]/button[1]'
#     # p_wait = wait.until(EC.element_to_be_clickable(By.XPATH, p_path))
#     p = driver.find_element(By.XPATH, p_path)
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
#     AutoLogin(driver, wait, "xhs_article")
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
#     interval = int(pb.config.get('Publish', 'interval'))
#     is_looped = pb.config.get('Publish', 'is_looped').lower() == "true"
#
#     main()

LOGIN_URL = "https://creator.xiaohongshu.com/publish/publish?source=official"


class XHSArticlePublisher(Publisher):
    def __init__(self):
        super().__init__(Platform.XHS, GenerateType.Article, LOGIN_URL)
    def _do_login(self) -> list:
        # 扫码登录
        login_ui_path = '//*[@id="page"]/div/div[2]/div[1]/div[2]/div/div/div/div/img'
        super().wait.until(EC.element_to_be_clickable((By.XPATH, login_ui_path)))
        elem = super().driver.find_element(By.XPATH, login_ui_path)
        elem.click()

    	# 确定为已登陆状态
    	# 首先先找到发布笔记，然后点击
    	publish_path = '//*[@id="content-area"]/main/div[1]/div/div[1]/a'
    	# 等待按钮找到
    	self.wait.until(EC.element_to_be_clickable((By.XPATH, publish_path)))

		time.sleep(3)

        # 获取Cookies并返回
        # super().wait.until(
        #    EC.presence_of_element_located((By.XPATH, '//*[@id="content-area"]/main/div[1]/div/div[1]/a')))
        return super().driver.get_cookies()

    def _get_user_name(self) -> str:
        # 获取用户名
        uid_element = super().driver.find_element(By.XPATH, '//*[@id="header-area"]/div/div/div[2]/div/span')
        return uid_element.text

    def _get_user_stat(self) -> dict:
        # 获取用户统计数据
        user_dict = {}
        # 获取关注数
        following_count_element = super().driver.find_element(By.XPATH,
                                                              '//*[@id="app"]/div/div[1]/div[1]/div[2]/p[1]/span[1]/label')
        following_count = int(following_count_element.text)
        user_dict['followingCount'] = following_count

        # 获取粉丝数
        follower_count_element = super().driver.find_element(By.XPATH,
                                                             '//*[@id="app"]/div/div[1]/div[1]/div[2]/p[1]/span[2]/label')
        follower_count = int(follower_count_element.text)
        user_dict['followerCount'] = follower_count

        # 打开数据看板
        next_click = super().driver.find_element(By.XPATH, '//*[@id="content-area"]/main/div[1]/div/div[2]/div/div[3]')
        next_click.click()
        # 打开笔记数据
        next_click = super().driver.find_element(By.XPATH, '//*[@id="content-area"]/main/div[1]/div/div[2]/div/div[4]')
        next_click.click()
        # 遍历笔记
        notes = super().driver.find_elements(By.XPATH, '//*[@id="app"]/div/div/div[3]/div')
        total_visit = 0
        total_like = 0
        total_collect = 0
        for note in notes:
            # li[1]观看量 li[2]点赞量 li[3]收藏量
            visit_count = note.find_element(By.XPATH, './div[2]/ul[1]/li[1]')
            total_visit = total_visit + int(visit_count.text)

            like_count = note.find_element(By.XPATH, './div[2]/ul[1]/li[2]')
            total_like = total_like + int(like_count.text)

            collect_count = note.find_element(By.XPATH, './div[2]/ul[1]/li[3]')
            total_collect = total_collect + int(collect_count.text)

        user_dict['likeCount'] = total_like
        user_dict['collectCount'] = total_collect
        user_dict['visitCount'] = total_visit
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

        content_tags = self.extract_content_tags(content_text.replace("\n", "<br/>"))

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



if __name__ == '__main__':
    publisher = XHSArticlePublisher()
    print("Start login...")
    publisher._do_login()
