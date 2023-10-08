import time
import subprocess
import pandas as pd
import requests
import os
import re
from pyppeteer import connect
import asyncio
import nest_asyncio
import pyppeteer
import socket
import tkinter as tk
from tkinter import messagebox
import platform
from tkinter import filedialog
import httpx
import threading

nest_asyncio.apply()


async def is_chrome_debugging_port_available(remote_debugging_port=9222):
    """
    判断 Chrome 浏览器是否处于 Debug 模式。

    参数:
    - int (remote_debugging_port): 调试端口号。

    返回:
    - bool: 如果浏览器处于 Debug 模式则返回 True，否则返回 False。
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://127.0.0.1:{remote_debugging_port}/json")
            response.raise_for_status()
            return True
    except httpx.RequestError:
        close_all_chrome_processes()
        return False


# 关闭所有 Chrome 进程
def close_all_chrome_processes():
    os_type = platform.system()

    if os_type == "Windows":
        subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    elif os_type == "Darwin":  # macOS
        cmd = ['osascript', '-e', 'tell application "Google Chrome" to quit']
        subprocess.run(cmd)
    else:
        raise EnvironmentError("Unsupported operating system")


def start_chrome_debugging(remote_debugging_port=9222):
    """
    判断 Chrome 浏览器是否启动。

    参数:
    - int (remote_debugging_port): 调试端口号。

    返回:
    - bool: 是否启动成功。
    """

    def is_port_open(port):
        """检查指定的端口是否已经打开"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0

    # 检查操作系统类型
    os_type = platform.system()
    if os_type == "Windows":
        # 请确保此路径指向您的Edge可执行文件
        command = f'start chrome --remote-debugging-port={remote_debugging_port}'
    elif os_type == "Darwin":  # macOS
        # 请确保此路径指向您的Edge可执行文件，这是默认路径
        command = f'open -a "Google Chrome" --args --remote-debugging-port={remote_debugging_port}'
    else:
        raise EnvironmentError("Unsupported operating system")

    subprocess.Popen(command, shell=True)
    time.sleep(2)  # 等待一会儿，确保Chrome已经启动

    # 尝试连接到Chrome调试端口，确保其已经启动
    retries = 0
    while retries < 5:
        if is_port_open(remote_debugging_port):
            return True
        time.sleep(1)  # 等待一秒再重试
        retries += 1

    return False


async def get_browser(remote_debugging_port=9222):
    """
    判断 Chrome 浏览器是否启动。

    参数:
    - int (remote_debugging_port): 调试端口号。

    返回:
    - bool: 连接后的浏览器对象。
    """
    # # 这里使用 await 确保函数完成后再继续
    if not await is_chrome_debugging_port_available(remote_debugging_port):
        start_chrome_debugging(remote_debugging_port)

    response = requests.get(f"http://127.0.0.1:{remote_debugging_port}/json/version")
    web_socket_url = response.json().get("webSocketDebuggerUrl")

    browser_connect = await connect(browserWSEndpoint=web_socket_url)
    return browser_connect


async def open_and_load_url_in_new_tab(target_url, browser):
    """
    在新标签页中打开并加载给定的URL，然后返回页面的标题。

    参数:
    - url (str): 要访问的页面URL。
    - browser (pyppeteer.browser.Browser): 已经连接或启动的浏览器实例

    返回:
    - tuple: 包括加载了指定URL的新标签页对象、页面标题。
    """
    # 获取所有已打开的页面
    pages = await browser.pages()

    # 如果页面数量大于3，则关闭除最后三个之外的页面
    if len(pages) > 3:
        for i in range(len(pages) - 3):  # 只保留最后三个页面
            try:
                if pages[i] not in await browser.pages():
                    continue
                await asyncio.sleep(0.5)
                await pages[i].close()
            except asyncio.exceptions.InvalidStateError:
                pass

    # 打开新页面
    page = await browser.newPage()
    await page.goto(target_url, timeout=60000)

    # 提取页面标题
    title = await page.title()

    return page, title


async def extract_social_metrics(page, web_url):
    """
    从给定的页面对象中提取用户昵称、IP属地、性别、年龄、关注数量、粉丝数量、获赞与收藏数量等信息

    参数:
    - page (pyppeteer.page.Page): 要从中提取社交指标的页面对象。
    - web_url (str): 页面的URL，用于决定如何提取指标。

    返回:
    - dict: 包含用户昵称、IP属地、年龄、性别、关注数量、粉丝数量和收藏数量的字典。
    """

    def convert_w_to_number(text):
        """
        将包含'w'或'万'的文本转换为整数。

        参数:
        - text (str): 要转换的文本。

        返回:
        - int: 转换后的整数。
        """
        if 'w' in text:
            return int(float(text.replace('w', '')) * 10000)
        elif '万' in text:
            return int(float(text.replace('万', '')) * 10000)
        else:
            return int(text)

    if "xiaohongshu" in web_url:
        await page.waitForSelector('div.info')
        await page.waitForSelector('.user-interactions')

        # 定义一个辅助函数来获取元素文本
        async def fetch_text(selector):
            element = await page.querySelector(selector)
            if element:
                return await page.evaluate('(e) => e.textContent', element)
            return None

        async def fetch_attr(selector, attribute_name):
            element = await page.querySelector(selector)
            if element:
                return await page.evaluate('(e, name) => e.getAttribute(name)', element, attribute_name)
            return None

        user_name = await fetch_text('div.user-name')
        user_redId = str(await fetch_text('span.user-redId')).split("：")[1] if await fetch_text(
            'span.user-redId') else None
        user_IP = str(await fetch_text('span.user-IP')).split("：")[1] if await fetch_text('span.user-IP') else None
        user_desc = await fetch_text('div.user-desc')

        # 提取性别
        gender_icon = await fetch_attr('.user-tags .tag-item .gender .reds-icon use', 'xlink:href')
        gender = "女" if gender_icon == "#female" else "男"  # 做了简化假设

        gender_text_content = await fetch_text('.user-tags .tag-item .gender .gender-text')
        age, constellation, location = None, None, None

        # 获取第二个tag-item的内容，可能是location
        potential_location = await fetch_text('.user-tags .tag-item:nth-child(2)')
        print(user_IP)
        print(potential_location)

        if gender_text_content:
            if "座" in gender_text_content:
                constellation = gender_text_content
            elif "岁" in gender_text_content:
                age = gender_text_content.replace("岁", "")
            if user_IP and isinstance(user_IP, str) and re.search(user_IP, potential_location or ''):
                location = potential_location.strip()

        follows = convert_w_to_number(await fetch_text(".user-interactions div:nth-child(1) .count"))
        fans = convert_w_to_number(await fetch_text(".user-interactions div:nth-child(2) .count"))
        likes_and_favorites = convert_w_to_number(await fetch_text(".user-interactions div:nth-child(3) .count"))

        metrics = {
            "用户昵称": user_name,
            "用户性别": gender,
            "用户年龄": age,
            "用户星座": constellation,
            "用户 IP": user_IP,
            "用户地点": location,
            "用户 ID": str(user_redId),
            "用户签名": user_desc,
            "用户关注": follows,
            "用户粉丝": fans,
            "用户点赞": likes_and_favorites
        }
        return metrics


async def process_and_save_to_excel(target_url, target_excel_path, metrics):
    try:
        # 使用线程锁确保写入操作不会导致数据混乱
        lock = threading.Lock()
        with lock:
            df = pd.read_excel(target_excel_path)

            # 如果列不存在则添加
            for column in metrics.keys():
                if column not in df.columns:
                    df[column] = None

            # 找到与 target_url 匹配的行
            idx = df[df['用户链接'] == target_url].index[0]

            # 更新该行的数据
            for key, value in metrics.items():
                df.at[idx, key] = value

            # 保存更新后的数据框
            df.to_excel(target_excel_path, index=False)

        print(f"Processed and updated data for {target_url}")

    except Exception as e:
        print(f"Error while processing URL {target_url}: {str(e)}")


async def process_all_urls(urls, target_excel_path, total_urls, processed_count):
    await is_chrome_debugging_port_available()
    browser = None
    try:
        browser = await get_browser()
        for url in urls:
            try:
                page, title = await open_and_load_url_in_new_tab(url, browser)
                print(title)
                metrics = await extract_social_metrics(page, url)
                await process_and_save_to_excel(url, target_excel_path, metrics)
                processed_count += 1
                progress = (processed_count / total_urls) * 100
                msg = f"共{total_urls}个用户，已爬取{processed_count}个用户，处理进度：{progress:.2f}%"
                msg_label.config(text=msg)
            except Exception as e:
                print(f"Error while processing URL {url}: {str(e)}")
    except Exception as e:
        print(f"Error while initializing browser: {str(e)}")
    finally:
        if browser:
            await browser.close()


def get_urls_to_process(excel_path):
    """
    读取 Excel 数据，返回需要爬取的URL列表

    参数:
    - excel_path (str): Excel 文件的路径

    返回:
    - list: 要爬取的URL列表
    """

    # 读取 Excel 数据
    excel_data = pd.read_excel(excel_path)

    # 初始化已处理的URL列表
    processed_urls = []

    # 检查 '用户链接' 列是否存在
    if '用户链接' not in excel_data.columns:
        raise ValueError("选择的Excel文件中没有'用户链接'列。请检查文件内容。")

    # 如果'用户昵称'列存在于数据中
    if '用户昵称' in excel_data.columns:
        # 获取“用户昵称”不为空的行对应的“用户链接”
        processed_urls = excel_data[excel_data['用户昵称'].notnull()]['用户链接'].drop_duplicates().tolist()

        # 只处理“用户昵称”为空的链接
        to_process_urls = excel_data[excel_data['用户昵称'].isnull()]['用户链接']
    else:
        # 如果没有“用户昵称”列，则处理所有链接
        to_process_urls = excel_data['用户链接']

    # 对用户链接数组进行去重
    to_process_urls = to_process_urls.drop_duplicates().tolist()

    # 去除掉之前已经爬取过有记录的用户链接
    to_process_urls = [url for url in to_process_urls if url not in processed_urls]

    total_urls = len(processed_urls) + len(to_process_urls)
    processed_count = len(processed_urls)
    return to_process_urls, total_urls, processed_count


def start_asyncio_tasks(urls, target_excel_path, total_urls, processed_count):
    asyncio.run(process_all_urls(urls, target_excel_path, total_urls, processed_count))


# 创建浏览文件的函数
def browse_file():
    file_path = filedialog.askopenfilename(title="选择评论源Excel文件",
                                           filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
    if file_path:
        try:
            info_label.config(text=f"选择的文件: {file_path}")
            # 如果没有异常，清空msg_label的内容
            msg_label.config(text="")
            urls_to_process, total_urls, processed_count = get_urls_to_process(file_path)
            # asyncio.run(process_all_urls(urls_to_process, file_path, total_urls, processed_count))
            threading.Thread(target=start_asyncio_tasks,
                             args=(urls_to_process, file_path, total_urls, processed_count)).start()
        except ValueError as e:  # 捕捉到'用户链接'列不存在的错误
            msg_label.config(text=str(e))


# 创建GUI窗口
window = tk.Tk()
window.title("智工评论抓取工具")

# 设置窗口大小
window.geometry("800x600")

# 创建按钮
selected_file_button = tk.Button(window, text="选择评论源Excel文件", command=browse_file)
selected_file_button.pack(pady=10)  # 添加垂直内边距

# 创建信息标签
info_label = tk.Label(window, text="", fg="white", background="grey")
info_label.pack(pady=10)

# 创建信息标签
msg_label = tk.Label(window, text="请选择任务文件夹中由评论处理工具处理后的合并 Excel 文件", fg="red")  # 使用红色字体作为警告提示
msg_label.pack(pady=10)

# 运行主循环
window.mainloop()