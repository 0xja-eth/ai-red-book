import re
import time
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver.chrome import ChromeDriverManager

import shutil
import os
import configparser

VIDEO_COUNT_FILE = "./vcount.txt"
PUB_VIDEO_COUNT_FILE = "./vpub_count.txt"

OUTPUT_ROOT = "./voutput"

driver: webdriver.Chrome
wait: WebDriverWait

# 读取配置文件
config = configparser.ConfigParser()
config.read('config.ini')

with open(VIDEO_COUNT_FILE, encoding="utf8") as vc_file:
    max_count = int(vc_file.read())

with open(PUB_VIDEO_COUNT_FILE, encoding="utf8") as vc_file:
    count = int(vc_file.read())


def get_title(idx):
    file_name = os.path.join(OUTPUT_ROOT, "%d-title.txt" % idx)
    with open(file_name, encoding="utf8") as file:
        return file.read()


def get_content(idx):
    file_name = os.path.join(OUTPUT_ROOT, "%d-content.txt" % idx)
    with open(file_name, encoding="utf8") as file:
        return file.read()


# 获取视频文件路径
def get_vi_abspath(idx):
    file_name = os.path.abspath(os.path.join(OUTPUT_ROOT, "%d-vi.mp4" % idx))
    if os.path.exists(file_name):
        return file_name
    raise Exception("File not exist: %s" % file_name)


def download_driver():
    chromedriver_path = ChromeDriverManager().install()

    # 将chromedriver移动到当前目录
    new_chromedriver_path = os.path.join(".", "chromedriver.exe")
    shutil.copy(chromedriver_path, new_chromedriver_path)


# 初始化浏览器驱动
def init_driver():
    global driver, wait

    if not os.path.exists("./chromedriver.exe"):
        download_driver()

    chromedriver_path = Service("./chromedriver.exe")
    driver = webdriver.Chrome(service=chromedriver_path)
    wait = WebDriverWait(driver, 120)


def extract_content_tags(text):
    segments = re.split(r'#\w+', text)
    hashtags = re.findall(r'#\w+', text)
    result = []

    for i in range(max(len(segments), len(hashtags))):
        if i < len(segments) and segments[i].strip() != '':
            result.append(segments[i].strip())
        if i < len(hashtags):
            result.append(hashtags[i])

    return result


def login():
    driver.get("https://creator.douyin.com/")
    # 登录之后采用如下代码输出cookie
    # for cookie in manual_cookies:
    #     print(cookie)
    #     driver.add_cookie(cookie)
    # driver.get("https://creator.xiaohongshu.com/publish/publish?source=official")
    # upload_img = driver.find_element(By.XPATH, "//*input[@type='file' and @class=‘upload-input’]")

    # time.sleep(60)

    # 扫码登录
    login_ui_path = '/html/body/div[1]/div/section/header/div[1]/div/div/div/div[2]/span'
    element = wait.until(EC.element_to_be_clickable((By.XPATH, login_ui_path)))
    elem = driver.find_element(By.XPATH, login_ui_path)
    elem.click()


# 发布视频
def publish():
    global count

    count = count % max_count + 1

    print("Start publish video: %d / %d" % (count, max_count))

    # 确定为已登录状态
    # 首先找到发布视频，然后点击
    publish_path = '/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[1]/button/span/span'
    # 等待按钮找到
    publish_wait = wait.until(EC.element_to_be_clickable((By.XPATH, publish_path)))
    publish = driver.find_element(By.XPATH, publish_path)
    publish.click()
    time.sleep(3)

    upload_video = driver.find_element(By.CLASS_NAME, "upload-btn-input--1NeEX")

    upload_video.send_keys(get_vi_abspath(count))

    # 等待视频上传完成
    while True:
        time.sleep(3)
        try:
            driver.find_element(By.CLASS_NAME, "upload-btn--9eZLd")
            break
        except Exception as e:
            print("视频还在上传中···")

    print("视频已上传完成！")

    # 需要再修改
    title_text = get_title(count)
    content_text = get_content(count)

    JS_CODE_ADD_TEXT = """
         console.log("arguments", arguments)
         var elm = arguments[0], txt = arguments[1], key = arguments[2] || "value";
         elm[key] += txt;
         elm.dispatchEvent(new Event('change'));
       """

    # 上传标题（抖音好像没有标题）
    # title_path = "c-input_inner"
    # title_elm = driver.find_element(By.CLASS_NAME, title_path)
    # driver.execute_script(JS_CODE_ADD_TEXT, title_elm, title_text)
    # time.sleep(3)


    # 上传内容
    content_tags = extract_content_tags(content_text.replace("\n", "<br/>"))

    content_path = '//*[@id="root"]/div/div/div[2]/div[1]/div[2]/div/div/div/div[1]/div'
    content_elm = driver.find_element(By.XPATH, content_path)
    driver.execute_script(JS_CODE_ADD_TEXT, content_elm,
                          content_text.replace("\n", "<br/>"), "innerHTML")
    time.sleep(3)

    for content_tag in content_tags:
        content_path = '//*[@id="root"]/div/div/div[2]/div[1]/div[2]/div/div/div/div[1]/div'
        content_elm = driver.find_element(By.XPATH, content_path)

        if content_tag.startswith("#"):
            topic_path = '//*[@id="root"]/div/div/div[2]/div[1]/div[2]/div/div/div[1]/div[2]/div[1]/div/div/div[1]'
            topic_elm = driver.find_element(By.XPATH, topic_path)
            topic_elm.click()

            content_tag = content_tag[1:]
            content_elm.send_keys(content_tag)
            time.sleep(3)
            content_elm.send_keys(Keys.ENTER)

        else:
            # 填写内容信息
            driver.execute_script(JS_CODE_ADD_TEXT, content_elm, content_tag, "innerHTML")
            # content.send_keys(description)

    time.sleep(3)

    # 上传
    p_path = '//*[@id="root"]/div/div/div[2]/div[1]/div[17]/button[1]'
    p_wait = wait.until(EC.element_to_be_clickable((By.XPATH, p_path)))
    p = driver.find_element(By.XPATH, p_path)
    p.click()
    # driver.find_element_by_xpath('//*[@id="root"]/div/div/div[2]/div[1]/div[17]/button[1]').click()

    with open(PUB_VIDEO_COUNT_FILE, "w", encoding="utf8") as file:
        file.write(str(count))

    print("End publish: %s: %s" % (title_text, content_text))


def main():
    init_driver()
    login()

    while True:
        try:
            publish()
            print(interval)
            time.sleep(interval)
        except Exception as e:
            print("Error publish: %s" % str(e))

        driver.refresh()
        if count >= max_count and not is_looped: break


if __name__ == '__main__':
    interval = int(config.get('DYPublish', 'interval'))
    is_looped = config.get('DYPublish', 'is_looped').lower() == "true"

    main()
