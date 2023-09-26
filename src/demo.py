
import asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
import json
import openai
from PIL import Image
import configparser

# 基本信息
# 图片存放路径
base_photo = r"D:\Coding\Exermon\RedBook\photo\01.jpg"
base_photo1 = r"D:\Coding\Exermon\RedBook\photo\02.jpg"
base_video = r"D:\Coding\Exermon\RedBook\video\测试.mp4"

# 描述
describe = "可爱的菜狗 #搞笑 #治愈 #动物"
titleContent = "小菜"


driver = webdriver.Chrome()
wait = WebDriverWait(driver, 120)

# 读取配置文件
config = configparser.ConfigParser()
config.read('config.ini')

# 获取API Key
openai_key = config.get('API', 'openai_key')

# 自动铺满
def resize_image(image, target_width, target_height):
    # 获取原始图片的宽度和高度
    width, height = image.size

    # 计算缩放比例
    width_ratio = target_width / width
    height_ratio = target_height / height
    ratio = max(width_ratio, height_ratio)

    # 计算调整后的图片尺寸
    new_width = int(width * ratio)
    new_height = int(height * ratio)

    # 缩放图片
    resized_image = image.resize((new_width, new_height), Image.LANCZOS)

    # 裁剪图片到目标尺寸
    left = (new_width - target_width) // 2
    top = (new_height - target_height) // 2
    right = left + target_width
    bottom = top + target_height
    resized_image = resized_image.crop((left, top, right, bottom))

    return resized_image


# 生成九宫格
def generateNineBlock() :
    images = [Image.open(f'./photo/0{i}.jpg') for i in range(1,10)]
    # 获取图片的宽高
    image_width, image_height = images[0].size

    # 创建新图片，尺寸为3倍的宽度和高度
    result_width = image_width * 3
    result_height = image_height * 3
    result_image = Image.new('RGB', (result_width, result_height))

    # 将九张图片按照九宫格排列拼接到新图片上
    for i in range(3):
        for j in range(3):
            resized_image = resize_image(images[i * 3 + j], image_width, image_height)
            result_image.paste(resized_image, (j * image_width, i * image_height))
    # 保存拼接后的图片
    result_image.save('./photo/result.jpg')

async def generateOpenAi1( prompt ) :
    openai.api_key = openai_key
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt= prompt,
        max_tokens=256,
    )
    message = response.choices[0].text
    new_message = message.replace(" ","")
    nmessage = new_message.strip()
    # print(message)
    # print("aaaaaaa")
    # print(new_message)
    # print("aaaaaaa")
    print(nmessage)
    return nmessage

async def test( vedioOrNot ):
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

    # time.sleep(8)

    # 确定为已登陆状态
    # 首先先找到发布笔记，然后点击
    publish_path = '//*[@id="content-area"]/main/div[1]/div/div[1]/a'
    # 等待按钮找到
    publish_wait = wait.until(EC.element_to_be_clickable((By.XPATH, publish_path)))
    publish = driver.find_element(By.XPATH, publish_path)
    publish.click()
    time.sleep(3)

    # 其次找到发布图片按钮
    if vedioOrNot == 0:
        upload_i_path0 = '//*[@id="publisher-dom"]/div/div[1]/div/div[1]/div[1]/div[2]'
        upload_wait = wait.until(EC.element_to_be_clickable((By.XPATH, upload_i_path0)))
        upload_i = driver.find_element(By.XPATH, upload_i_path0)
        upload_i.click()
        time.sleep(3)

    # 输入按钮
    upload_all = driver.find_element(By.CLASS_NAME, "upload-input")
    if vedioOrNot == 0:
        upload_all.send_keys(base_photo)
        upload_all.send_keys(base_photo1)
        time.sleep(15)
        print("已经上传图片")

        # 填写标题
        title_path = '//*[@id="publisher-dom"]/div/div[1]/div/div[2]/div[2]/div[2]/input'
        title = driver.find_element(By.XPATH, title_path)
        title_content = await generateOpenAi1("请你随机生成一个关于小黑子的标题，不超过10个字")
        title.send_keys(title_content)
        time.sleep(3)

        # 填写内容信息
        content_path = '//*[@id="post-textarea"]'
        descripition = await generateOpenAi1("请你随机生成一段30字的关于小黑子的文案")
        content = driver.find_element(By.XPATH, content_path)
        content.send_keys(descripition)
        time.sleep(3)

        # 发布内容
        p_path = '//*[@id="publisher-dom"]/div/div[1]/div/div[2]/div[2]/div[7]/button[1]'
        pp_path = '//*[@id="publisher-dom"]/div/div[1]/div/div[2]/div[2]/div[7]/button[1]'
        # p_wait = wait.until(EC.element_to_be_clickable(By.XPATH, p_path))
        p = driver.find_element(By.XPATH, p_path)
        p.click()

        time.sleep(10)

        await rePublishPhoto()

    else:
        upload_all.send_keys(base_video)
        # 填写标题
        # title_path = '//*[@id="publish-container"]/div/div[3]/div[2]/div[3]/input'
        title = driver.find_element(By.CLASS_NAME, "c-input_inner")
        title.send_keys(titleContent)
        time.sleep(3)
        # 填写内容
        content_path = '//*[@id="post-textarea"]'
        content = driver.find_element(By.XPATH, content_path)
        content.send_keys(describe)
        time.sleep(3)
        # 发布内容
        p_path = '//*[@id="publish-container"]/div/div[3]/div[2]/div[9]/button[1]'
        p_wait = wait.until(EC.element_to_be_clickable((By.XPATH,p_path)))
        p = driver.find_element(By.XPATH, p_path)
        p.click()

async def rePublishPhoto() :
    upload_i_path0 = '//*[@id="publisher-dom"]/div/div[1]/div/div[1]/div[1]/div[2]'
    upload_wait = wait.until(EC.element_to_be_clickable((By.XPATH, upload_i_path0)))
    upload_i = driver.find_element(By.XPATH, upload_i_path0)
    upload_i.click()
    time.sleep(3)

    upload_all = driver.find_element(By.CLASS_NAME, "upload-input")

    upload_all.send_keys(base_photo)
    upload_all.send_keys(base_photo1)
    time.sleep(10)
    print("已经上传图片")

    # 填写标题
    title_path = '//*[@id="publisher-dom"]/div/div[1]/div/div[2]/div[2]/div[2]/input'
    title = driver.find_element(By.XPATH, title_path)
    title_content = await generateOpenAi1("请你随机生成一个关于小黑子的标题,不超过10个字")
    title.send_keys(title_content)
    time.sleep(3)

    # 填写内容信息
    content_path = '//*[@id="post-textarea"]'
    descripition = await generateOpenAi1("请你随机生成一段30字的关于小黑子的文案")
    content = driver.find_element(By.XPATH, content_path)
    content.send_keys(descripition)
    time.sleep(3)

    # 发布内容
    p_path = '//*[@id="publisher-dom"]/div/div[1]/div/div[2]/div[2]/div[7]/button[1]'
    p = driver.find_element(By.XPATH, p_path)
    p.click()


if __name__ == '__main__':
    # generateNineBlock()
    # driver.close()
    # asyncio.run(generateOpenAi1("请你随机生成一段30字的关于小黑子的文案"))
    asyncio.run(test(0))


