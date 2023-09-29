import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import os
def load_cookies(platform):
    cookiesFilename = "./"+platform+"_cookies.json"
    #检测是否存在cookies文件
    if not os.path.exists(cookiesFilename):
        return []
    #返回cookies
    with open(cookiesFilename, "r", encoding="utf8") as file:
        cookies = json.load(file)
    return cookies

def save_cookies(driver,platform):
    cookiesFilename = "./" + platform + "_cookies.json"
    cookies = driver.get_cookies()
    # print("cookies:", cookies)
    #清空cookies文件
    with open(cookiesFilename, "w", encoding="utf8") as file:
        file.truncate()
    with open(cookiesFilename, "w", encoding="utf8") as file:
        json.dump(cookies, file)

def AutoLogin(driver, wait, platform):
    publish_element=""
    if(platform == "xhs_article" or platform == "xhs_video"):
        # 小红书发布的按钮
        publish_element = '//*[@id="content-area"]/main/div[1]/div/div[1]/a'
        driver.get("https://creator.xiaohongshu.com/")
        # 扫码登录
        login_ui_path = '//*[@id="page"]/div/div[2]/div[1]/div[2]/div/div/div/div/img'
        element = wait.until(EC.element_to_be_clickable((By.XPATH, login_ui_path)))
        elem = driver.find_element(By.XPATH, login_ui_path)
        elem.click()
    elif(platform == "dy_video"):

        # 抖音视频号发布的按钮
        publish_element = '//*[@id="root"]/div/div[2]/div[2]/div/div/div/div[1]/button'
        driver.get("https://creator.douyin.com/")
        # 扫码登录
        login_ui_path = '/html/body/div[1]/div/section/header/div[1]/div/div/div/div[2]/span'
        element = wait.until(EC.element_to_be_clickable((By.XPATH, login_ui_path)))
        elem = driver.find_element(By.XPATH, login_ui_path)
        elem.click()
    elif(platform == "wx_video"):
        # 微信视频号发布的按钮
        publish_element = "//div[@class='weui-desktop-btn weui-desktop-btn_primary']"
        driver.get("https://channels.weixin.qq.com/login.html")
    else:
        print("platform error")

    cookies = load_cookies(platform)
    for cookie in cookies:
        driver.add_cookie(cookie)
    driver.refresh()
    # 确保登陆成功后（出现发布按钮）保存cookies：
    wait.until(EC.presence_of_element_located((By.XPATH, publish_element)))
    save_cookies(driver, platform)

# TODO: [莫倪] 将这里的内容转移到各个publisher里面，这个文件就可以删掉了