import base64

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
import os
import shutil
import time

VIDEO_ROOT = "./voutput"

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
    # driver.find_element().send_keys()
    wait = WebDriverWait(driver, 120)

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

    # time.sleep(20)

    # JS.Click()
    JS_Click = """
    arguments[0].click()
    """

    # # 点击内容管理
    # cManage_path = 'weui-desktop-menu__link.weui-desktop-menu__sub__link'
    # cManage_wait = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, cManage_path)))
    # cManage = driver.find_element(By.CLASS_NAME, cManage_path)
    # cManage.click()
    #
    # time.sleep(20)
    #
    # # 点击视频管理
    # vManage_path = 'weui-desktop-menu__link.weui-desktop-menu__only-icon'
    # vManage_wait = wait.Until()
    # vManage = driver.find_element(By.CLASS_NAME, vManage_path)
    # vManage.click()
    #
    # time.sleep(10)

    cManage_path = 'weui-desktop-menu__link.weui-desktop-menu__sub__link'
    cManage_wait = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, cManage_path)))

    time.sleep(3)

    # 点击发布视频
    publish_path = '//*[@id="container-wrap"]/div[2]/div/div[2]/div[3]/div[1]/div/div[1]/div[2]/div/button'
    # 等待按钮找到
    # publish_wait = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, publish_path)))
    publish = driver.find_element(By.XPATH, publish_path)
    driver.execute_script(JS_Click, publish)

    time.sleep(3)
    # 上传新视频
    # 将视频文件转化为二进制文件
    with open(get_vi_abspath(1), 'rb') as video_file:
        video_binary = video_file.read()

    video_base64 = base64.b64encode(video_binary).decode('utf-8')

    JS_VIDEO_ADD = """
    console.log("arguments", arguments)
    var elm = arguments[0], video = arguments[1];
    var file = new File([video], "video.mp4", {type: "video/mp4"});
    Object.defineProperty(elm, "files", {
        value: [file],
        writable: true,
    });
    elm.dispatchEvent(new Event('change', { bubbles: true }));
    """

    # 设置为可见
    JS_VIDSABLE = """
    arguments[0].style.display = 'block';
    """
    JS_INPUT_VISABLE = """
    var input = document.querySelector('input');
    input.style.display = 'block';
    """

    pVideo_path = 'upload-content'
    # pVideo_path = 'input[type="file"]'
    # pVideo_path = 'input'
    # pVideo_wait = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, pVideo_path)))
    pVideo = driver.find_element(By.CLASS_NAME, pVideo_path)

    driver.execute_script(JS_INPUT_VISABLE)

    pNVideo_path = 'input'
    pNVideo = driver.find_element(By.CSS_SELECTOR, pNVideo_path)

    pNVideo.send_keys(get_vi_abspath(1))
    time.sleep(1)
    # TODO 需要再改vx_count
    # driver.execute_script(f"arguments[0].value = '{get_vi_abspath(0)}", pVideo)
    # print(video_binary)


    # driver.execute_script(JS_VIDEO_ADD, pVideo, video_base64)

    # driver.execute_script(JS_VIDSABLE, pVideo)

    # pVideo.send_keys(get_vi_abspath(0))

    # 等待视频上传完成
    while True:
        time.sleep(3)
        try:
            driver.find_element(By.CLASS_NAME, "ant-progress-inner")
            print("视频还在上传中……")
        except Exception as e:
            break

    print("视频上传完成!")


    # TODO 需要具体内容
    title = "测试测试测试测试"
    content = "测试1111"

    JS_CODE_ADD_TEXT = """
            console.log("arguments", arguments)
            var elm = arguments[0], txt = arguments[1], key = arguments[2] || "textContent";
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

    driver.execute_script(JS_VIDSABLE, title_publish)
    time.sleep(1)
    title_publish.send_keys(title)
    # driver.execute_script(JS_CODE_ADD_TEXT, title_publish, title)
    time.sleep(3)


def main():
    init_driver()
    login()
    publish()

if __name__ == '__main__':
    main()