import base64

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

import os
import shutil
import time
import configparser

VIDEO_COUNT_FILE = "vxcount.txt"
PUB_VIDEO_COUNT_FILE = "vxpub_count.txt"

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


def init_driver():
    global driver, wait

    if not os.path.exists("./chromedriver.exe"):
        download_driver()

    chromedriver_path = Service("./chromedriver.exe")
    driver = webdriver.Chrome(service=chromedriver_path)
    wait = WebDriverWait(driver, 120)


def login():
    # 网页打开后扫码登录
    driver.get("https://channels.weixin.qq.com/login.html")


def publish():
    # TODO 注意此处需要结合小红书中的video进行上传修改count
    global count

    count = count % max_count + 1

    print("Start publish video: %d / %d" % (count, max_count))

    JS_CLICK = """
    arguments[0].click()
    """

    c_manage_path = 'weui-desktop-menu__link.weui-desktop-menu__sub__link'
    wait.until(EC.element_to_be_clickable((By.CLASS_NAME, c_manage_path)))

    time.sleep(3)

    # 点击发布视频
    if count == 1:
        publish_path = '//*[@id="container-wrap"]/div[2]/div/div[2]/div[3]/div[1]/div/div[1]/div[2]/div/button'
        publish_ele = driver.find_element(By.XPATH, publish_path)
        driver.execute_script(JS_CLICK, publish_ele)
    else:
        publish_path = 'weui-desktop-btn.weui-desktop-btn_primary'
        publish_eles = driver.find_elements(By.CLASS_NAME, publish_path)
        publish_ele = publish_eles[1]
        driver.execute_script(JS_CLICK, publish_ele)


    time.sleep(3)

    # 设置输入为可见
    JS_INPUT_VISABLE = """
    var input = document.querySelector('input');
    input.style.display = 'block';
    """

    driver.execute_script(JS_INPUT_VISABLE)

    p_video_path = 'input'
    p_video = driver.find_element(By.CSS_SELECTOR, p_video_path)
    p_video.send_keys(get_vi_abspath(1))

    time.sleep(1)

    # 等待视频上传完成
    while True:
        time.sleep(3)
        try:
            driver.find_element(By.CLASS_NAME, "ant-progress-inner")
            print("视频还在上传中……")
        except Exception as e:
            break

    print("视频上传完成!")

    title_text = get_title(count)
    content_text = get_content(count)

    time.sleep(3)

    # TODO 判断是否不显示位置
    if True:
        location_path = 'option-item.active'
        location_none = driver.find_element(By.CLASS_NAME, location_path)
        driver.execute_script(JS_CLICK, location_none)

    JS_CODE_ADD_TEXT = """
            console.log("arguments", arguments)
            var elm = arguments[0], txt = arguments[1], key = arguments[2] || "value";
            elm[key] += txt;
            elm.dispatchEvent(new Event('change'));
          """

    # 上传视频描述
    description_path = "input-editor"
    description_publish = driver.find_element(By.CLASS_NAME, description_path)
    description_key = "textContent"

    driver.execute_script(JS_CODE_ADD_TEXT, description_publish, content_text, description_key)

    time.sleep(3)

    title_path = 'weui-desktop-form__input'
    title_publishs = driver.find_elements(By.CLASS_NAME, title_path)

    title_publish = title_publishs[3]

    # driver.execute_script(JS_VIDSABLE, title_publish)
    # time.sleep(1)
    # title_publish[1].send_keys(title)
    driver.execute_script(JS_CODE_ADD_TEXT, title_publish, title_text)

    time.sleep(3)

    # 发送
    confirm_path = 'weui-desktop-btn.weui-desktop-btn_primary'
    confirms = driver.find_elements(By.CLASS_NAME, confirm_path)
    confirm = confirms[7]
    driver.execute_script(JS_CLICK, confirm)

    with open(PUB_VIDEO_COUNT_FILE, "w", encoding="utf8") as file:
        file.write(str(count))

    print("End publish: %s: %s" % (title_text, content_text))


def main():
    init_driver()
    login()

    while True:
        try:
            publish()
            time.sleep(interval)
        except Exception as e:
            print("Error publish: %s" % str(e))

        driver.refresh()
        if count >= max_count and not is_looped: break


if __name__ == '__main__':
    interval = int(config.get('VPublish', 'interval'))
    is_looped = config.get('VPublish', 'is_looped').lower() == "true"

    main()
