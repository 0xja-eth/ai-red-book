
import asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import configparser

COUNT_FILE = "./pub_count.txt"

OUTPUT_ROOT = "./output"

with open(COUNT_FILE, encoding="utf8") as c_file:
    count = int(c_file.read())

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 120)

# 读取配置文件
config = configparser.ConfigParser()
config.read('config.ini')


def get_title(idx=count):
    file_name = os.path.join(OUTPUT_ROOT, "%d-title.txt" % idx)
    with open(file_name, encoding="utf8") as file:
        return file.read()


def get_content(idx=count):
    file_name = os.path.join(OUTPUT_ROOT, "%d-content.txt" % idx)
    with open(file_name, encoding="utf8") as file:
        return file.read()


def get_pic_path(idx=count):
    return os.path.join(OUTPUT_ROOT, "%d-pic.jpg" % idx)


async def login():
    driver.get("https://creator.xiaohongshu.com/publish/publish?source=official")
    # 登录之后采用如下代码输出cookie
    # for cookie in manual_cookies:
    #     print(cookie)
    #     driver.add_cookie(cookie)
    # driver.get("https://creator.xiaohongshu.com/publish/publish?source=official")
    # upload_img = driver.find_element(By.XPATH, "//*input[@type='file' and @class=‘upload-input’]")

    # time.sleep(60)

    # 扫码登录
    login_ui_path = '//*[@id="page"]/div/div[2]/div[1]/div[2]/div/div/div/div/img'
    element = wait.until(EC.element_to_be_clickable((By.XPATH, login_ui_path)))
    elem = driver.find_element(By.XPATH, login_ui_path)
    elem.click()


async def publish():
    global count

    count += 1

    # 确定为已登陆状态
    # 首先先找到发布笔记，然后点击
    publish_path = '//*[@id="content-area"]/main/div[1]/div/div[1]/a'
    # 等待按钮找到
    publish_wait = wait.until(EC.element_to_be_clickable((By.XPATH, publish_path)))
    publish = driver.find_element(By.XPATH, publish_path)
    publish.click()
    time.sleep(3)

    # 输入按钮
    upload_all = driver.find_element(By.CLASS_NAME, "upload-input")

    upload_all.send_keys(get_pic_path())
    # upload_all.send_keys(base_photo1)
    time.sleep(15)
    print("已经上传图片")

    # 填写标题
    title_path = '//*[@id="publisher-dom"]/div/div[1]/div/div[2]/div[2]/div[2]/input'
    title = driver.find_element(By.XPATH, title_path)
    title_content = get_title()
    title.send_keys(title_content)
    time.sleep(3)

    # 填写内容信息
    content_path = '//*[@id="post-textarea"]'
    description = get_content()
    content = driver.find_element(By.XPATH, content_path)
    content.send_keys(description)
    time.sleep(3)

    # 发布内容
    p_path = '//*[@id="publisher-dom"]/div/div[1]/div/div[2]/div[2]/div[7]/button[1]'
    pp_path = '//*[@id="publisher-dom"]/div/div[1]/div/div[2]/div[2]/div[7]/button[1]'
    # p_wait = wait.until(EC.element_to_be_clickable(By.XPATH, p_path))
    p = driver.find_element(By.XPATH, p_path)
    p.click()

    time.sleep(10)

    with open(COUNT_FILE, "w", encoding="utf8") as file:
        file.write(str(count))


async def main():
    await login()
    await publish()


if __name__ == '__main__':
    asyncio.run(main())


