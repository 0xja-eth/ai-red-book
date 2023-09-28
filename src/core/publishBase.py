import time
import re
import json
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

import shutil
import os
import configparser


count_dict={
    'maxcount': 7,
    'count': 6
}


with open('../count.json', 'r') as count_read_file:
    count_dict = json.load(count_read_file)
    max_count = count_dict['maxcount']
    count = count_dict['count']

OUTPUT_ROOT = "../output/video"

driver: webdriver.Chrome
wait: WebDriverWait

# 读取配置文件
config = configparser.ConfigParser()
config.read('../config.ini')

def set_count(str, num):
    count_dict[str] = num
    with open('./count.json', 'w') as count_write_file:
        json.dump(count_dict, count_write_file)
        get_count()

def get_count():
    global max_count, count, count_dict
    with open('../count.json', 'r') as read_file:
        count_dict = json.load(read_file)
        max_count = count_dict['maxcount']
        count = count_dict['count']

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