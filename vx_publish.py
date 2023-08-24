from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException
import os
import shutil
import time

VIDEO_ROOT = "./video"

VX_VIDEO_COUNT_FILE = "vx_count.txt"
PUB_VX_VIDEO_COUNT_FILE = "vx_pub_count.txt"

driver = None
wait = None

with open(VX_VIDEO_COUNT_FILE, encoding="utf8") as vc_file:
    vx_max_count = int(vc_file.read())

with open(PUB_VX_VIDEO_COUNT_FILE, encoding="utf8") as vc_file:
    vx_count = int(vc_file.read())

def get_vi_abspath(idx):
    file_name = os.path.abspath(os.path.join(VIDEO_ROOT, "%d-vi.mp4" % idx))
    if os.path.exists(file_name): return file_name
    raise Exception("File not exist: %s " % file_name)

def init_driver():
    global driver, wait
    if not os.path.exists("./chromedriver.exe"):
        download_driver()

    chromedriver_path = Service("./chromedriver.exe")
    driver = webdriver.Chrome(service=chromedriver_path)
    wait = WebDriverWait(driver, 20)

def download_driver():
    chromedriver_path = ChromeDriverManager().install()

    # 将chromedriver移动到当前目录
    new_chromedriver_path = os.path.join(".", "chromedriver.exe")
    shutil.copy(chromedriver_path, new_chromedriver_path)


def login():
    # 网页打开后扫码登录
    driver.get("https://channels.weixin.qq.com/login.html")

def publish():
    # TODO 注意此处需要结合小红书中的video进行上传修改count
    global vx_count

    vx_count = vx_count % vx_max_count + 1

    print("Start publish video: %d / %d" % (vx_count, vx_max_count))

    time.sleep(20)

    # 点击内容管理
    cManage_path = 'weui-desktop-menu__link.weui-desktop-menu__sub__link'
    cManage = driver.find_element(By.CLASS_NAME, cManage_path)
    cManage.click()

    time.sleep(20)

    # 点击视频管理
    vManage_path = 'weui-desktop-menu__link.weui-desktop-menu__only-icon'
    vManage = driver.find_element(By.CLASS_NAME, vManage_path)
    vManage.click()

    time.sleep(10)

    # 点击发布视频
    publish_path = 'weui-desktop-btn.weui-desktop-btn_primary'
    # 等待按钮找到
    # publish_wait = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, publish_path)))
    publish = driver.find_element(By.CLASS_NAME, publish_path)
    publish.click()
    time.sleep(3)

    # 上传新视频
    pVideo_path = 'upload-content'
    pVideo_wait = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, pVideo_path)))
    pVideo = driver.find_element(By.CLASS_NAME, pVideo_path)

    pVideo.send_keys(get_vi_abspath(vx_count))

    # 等待视频上传完成
    while True:
        time.sleep(3)
        try:
            driver.find_element(By.CLASS_NAME, "ant-progress-inner")
            break
        except Exception as e:
            print("视频还在上传中……")

    print("视频上传完成!")


    # TODO 需要具体内容
    title = "测试"
    content = "测试1111"

    JS_CODE_ADD_TEXT = """
            console.log("arguments", arguments)
            var elm = arguments[0], txt = arguments[1], key = arguments[2] || "value";
            elm[key] += txt;
            elm.dispatchEvent(new Event('change'));
          """

    # 上传视频描述
    description_path = "input-editor"
    description_publish = driver.find_element(By.CLASS_NAME, description_path)

    driver.execute_script(JS_CODE_ADD_TEXT, description_publish, content)
    time.sleep(3)

    title_path = "weui-desktop-form__input"
    title_publish = driver.find_element(By.CLASS_NAME, title_path)

    driver.execute_script(JS_CODE_ADD_TEXT, title_publish, title)
    time.sleep(3)


def main():
    init_driver()
    login()
    publish()

if __name__ == '__main__':
    main()