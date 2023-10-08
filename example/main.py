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


async def extract_social_metrics(page, web_url):
    """
    从给定的页面对象中提取点赞、评论和收藏数量。

    参数:
    - page (pyppeteer.page.Page): 要从中提取社交指标的页面对象。
    - web_url (str): 页面的URL，用于决定如何提取指标。

    返回:
    - dict: 包含点赞、评论和收藏数量的字典。
    """

    metrics = {
        "likes": 0,
        "comments": 0,
        "collects": 0
    }

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

    if "douyin" in web_url:
        # 获取所有匹配选择器的元素
        elements = await page.querySelectorAll('div.kr4MM4DQ > span.CE7XkkTw')

        if len(elements) >= 1:  # 确保至少有一个元素
            likes_text = await page.evaluate('(element) => element.textContent', elements[0])
            metrics["likes"] = convert_w_to_number(likes_text)

        if len(elements) >= 2:  # 确保至少有两个元素
            comments_text = await page.evaluate('(element) => element.textContent', elements[1])
            metrics["comments"] = convert_w_to_number(comments_text)

        if len(elements) >= 3:  # 确保至少有三个元素
            shares_text = await page.evaluate('(element) => element.textContent', elements[2])
            metrics["collects"] = convert_w_to_number(shares_text)

    elif "xiaohongshu" in web_url:
        await page.waitForSelector('div.interactions')
        interactions_div = await page.querySelector('div.interactions')
        print(interactions_div)
        if interactions_div:
            likes_element = await page.querySelector(
                'div.interactions > div.buttons > div.left > span.like-wrapper > span.count')
            collects_element = await page.querySelector(
                'div.interactions > div.buttons > div.left > span.collect-wrapper > span.count')
            comments_element = await page.querySelector(
                'div.interactions > div.buttons > div.left > span.chat-wrapper > span.count')

            if likes_element:
                likes_text = await page.evaluate('(element) => element.textContent', likes_element)
                metrics["likes"] = convert_w_to_number(likes_text)

            if collects_element:
                collects_text = await page.evaluate('(element) => element.textContent', collects_element)
                metrics["collects"] = convert_w_to_number(collects_text)

            if comments_element:
                comments_text = await page.evaluate('(element) => element.textContent', comments_element)
                metrics["comments"] = convert_w_to_number(comments_text)


    elif "bilibili" or "b23" in web_url:
        # 等待评论加载
        await asyncio.sleep(3)
        await page.waitForSelector("div.reply-navigation", timeout=10000)

        # 获取点赞数量
        likes_element = await page.querySelector(".video-like-info.video-toolbar-item-text")
        if likes_element:
            likes_text = await page.evaluate('(element) => element.textContent', likes_element)
            metrics["likes"] = convert_w_to_number(likes_text)

        # 获取收藏数量
        fav_element = await page.querySelector(".video-fav-info.video-toolbar-item-text")
        if fav_element:
            fav_text = await page.evaluate('(element) => element.textContent', fav_element)
            metrics["collects"] = convert_w_to_number(fav_text)

        # 获取评论数量
        comments_element = await page.querySelector("div.reply-navigation li.nav-title span.total-reply")
        if comments_element:
            comments_text = await page.evaluate('(element) => element.textContent', comments_element)
            metrics["comments"] = convert_w_to_number(comments_text)

    else:
        print("URL doesn't contain 'douyin', 'xiaohongshu', or 'bilibili'")

    return metrics


async def open_and_load_url_in_new_tab(url, browser):
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
    await page.goto(url, timeout=60000)

    # 提取页面标题
    title = await page.title()

    return page, title


async def click_element_by_class(page, element_class_name):
    try:
        # 等待元素出现在DOM中
        await page.waitForSelector(f'.{element_class_name}', {'timeout': 10000})  # 10秒超时

        # 确保元素可见并可交互
        await page.waitForFunction('''selector => {
            const element = document.querySelector(selector);
            return element &&
                getComputedStyle(element).visibility === 'visible' &&
                element.getBoundingClientRect().height > 0;
        }''', {}, f'.{element_class_name}')

        # 点击元素
        await page.click(f'.{element_class_name}')

        return {'success': True}
    except Exception as e:
        print(f"Error clicking element by class: {e}")
        return {'success': False}


async def press_keys(page, keys, end_condition, end_condition_values, delay=0.01):
    """
    在页面上同时按下一组按键，直到满足结束条件。

    参数:
    - page (pyppeteer.page.Page): 要在其上按键的页面对象。
    - keys (list): 要同时按下的按键列表。
    - end_condition (str): 结束按键的条件，可以是 "出现某些元素"、"持续一定时间" 或 "出现某些文字"。
    - end_condition_values (list): 根据结束条件，可以是 CSS 类列表、持续时间或要检查的文本列表。

    返回:
    - dict: 包含操作是否成功的标志及任何错误信息。
    """

    # should_stop = False
    # end_time = None

    async def press_keys_repeatedly():
        should_stop = False
        end_time = None

        if end_condition == "持续一定时间":
            end_time = asyncio.get_event_loop().time() + float(end_condition_values[0])

        while not should_stop:
            for key in keys:  # 按下所有按键
                await page.keyboard.down(key)
            if end_condition in ["出现某些元素", "出现某些文字"]:
                should_stop = await check_end_condition()
                # print(should_stop)
                if should_stop:
                    break
            elif end_condition == "持续一定时间":
                if asyncio.get_event_loop().time() >= end_time:
                    should_stop = True
            await asyncio.sleep(delay)

        # print("stop")
        await asyncio.sleep(0.5)
        for key in keys:  # 释放所有按键
            await page.keyboard.up(key)
        return

    async def check_end_condition():
        os_type = platform.system()
        timeout_value = 50

        if os_type == "Darwin":
            timeout_value = 50

        if end_condition == "出现某些元素":
            for css_class in end_condition_values:
                try:
                    element = await page.querySelector('.end-container')
                    if element:
                        # print(css_class)
                        return True
                    else:
                        continue
                except Exception as e:
                    print(f"Error while checking for element .{css_class}: {str(e)}")

                continue
            return False
        elif end_condition == "出现某些文字":
            for text in end_condition_values:
                try:
                    await page.waitForFunction(f'document.body.innerText.includes("{text}")',
                                               {'timeout': timeout_value})
                    return True
                except pyppeteer.errors.TimeoutError:
                    continue
            return False
        return False

    try:
        await press_keys_repeatedly()
        return {'success': True}
    except Exception as e:
        errorMsg = f"Failed to press keys {', '.join(keys)}: {str(e)}"
        print(errorMsg)
        return {'success': False, 'error': errorMsg}


async def fetch_comments(page, element_class_name):
    """
    从提供的页面中提取评论。

    参数:
    - page (pyppeteer.page.Page): 已经打开和加载的页面实例。
    - element_class_name (str): 要从中提取评论的元素的类名。

    返回:
    - dict: 包含操作是否成功的标志、数据或错误信息。
    """
    if not page:
        errorMsg = "Page not provided."
        print(errorMsg)
        return {"success": False, "error": errorMsg}

    try:
        # 获取评论
        elements = await page.querySelectorAll(f'.{element_class_name}')
        extracted_comments = []
        for element in elements:
            text_content = await page.evaluate('(element) => element.innerText.trim()', element)
            extracted_comments.append(text_content)

        # 过滤空评论并去重
        filtered_comments = list(set([comment for comment in extracted_comments if comment != '']))

        return {"success": True, "data": filtered_comments}

    except Exception as error:
        errorMsg = f"Failed to fetch comments: {str(error)}"
        print(errorMsg)
        return {"success": False, "error": errorMsg}


async def fetch_red_book_comments_and_likes(page, element_class_name="comment-inner-container"):
    """
    从提供的页面中提取评论和点赞数量。

    参数:
    - page (pyppeteer.page.Page): 已经打开和加载的页面实例。
    - element_class_name (str): 要从中提取评论和点赞数量的元素的类名，默认为"comment-inner-container"。

    返回:
    - dict: 包含操作是否成功的标志、数据或错误信息。
    """
    if not page:
        errorMsg = "Page not provided."
        print(errorMsg)
        return {"success": False, "error": errorMsg}

    try:
        print("开始抓去")
        # 获取评论和点赞
        elements = await page.querySelectorAll(f'.{element_class_name}')
        extracted_data = {}
        for element in elements:
            content_element = await element.querySelector('.content')
            like_element = await element.querySelector('.like .like-wrapper.like-active')  # 选择有活跃状态的点赞元素

            if content_element:
                text_content = await page.evaluate('(element) => element.innerText.trim()', content_element)
                if like_element:
                    # 如果找不到count元素，但like-wrapper元素是活跃的，那么点赞数可能是1
                    likes = 1
                    count_element = await like_element.querySelector('.count')
                    if count_element:  # 如果确实有count元素，更新点赞数
                        likes = int(await page.evaluate('(element) => element.innerText.trim()', count_element))
                    extracted_data[text_content] = likes
                else:
                    extracted_data[text_content] = 0

        return {"success": True, "data": extracted_data}

    except Exception as error:
        errorMsg = f"Failed to fetch comments and likes: {str(error)}"
        print(errorMsg)
        return {"success": False, "error": errorMsg}


async def fetch_douyin_comments_and_likes(page, element_class_name="RHiEl2d8"):
    """
    从提供的页面中提取评论和点赞数量。

    参数:
    - page (pyppeteer.page.Page): 已经打开和加载的页面实例。
    - element_class_name (str): 要从中提取评论和点赞数量的元素的类名，默认为"RHiEl2d8"。

    返回:
    - dict: 包含操作是否成功的标志、数据或错误信息。
    """
    if not page:
        errorMsg = "Page not provided."
        print(errorMsg)
        return {"success": False, "error": errorMsg}

    try:
        # 获取评论和点赞
        elements = await page.querySelectorAll(f'.{element_class_name}')
        extracted_data = {}
        for element in elements:
            content_element = await element.querySelector('.a9uirtCT')
            like_element = await element.querySelector('.eJuDTubq span')

            if content_element:
                text_content = await page.evaluate('(element) => element.innerText.trim()', content_element)
                if like_element:
                    likes = await page.evaluate('(element) => element.innerText.trim()', like_element)
                    extracted_data[text_content] = int(likes)
                else:
                    extracted_data[text_content] = 0

        return {"success": True, "data": extracted_data}

    except Exception as error:
        errorMsg = f"Failed to fetch comments and likes: {str(error)}"
        print(errorMsg)
        return {"success": False, "error": errorMsg}


async def fetch_bilibili_comments_and_likes(page, primary_class_name="root-reply-container",
                                            secondary_class_name="sub-reply-item"):
    """
    从提供的页面中提取Bilibili的评论和点赞数量。

    参数:
    - page (pyppeteer.page.Page): 已经打开和加载的页面实例。
    - primary_class_name (str): 要从中提取主评论和点赞数量的元素的类名，默认为"root-reply-container"。
    - secondary_class_name (str): 要从中提取子评论和点赞数量的元素的类名，默认为"sub-reply-item"。

    返回:
    - dict: 包含操作是否成功的标志、数据或错误信息。
    """
    if not page:
        errorMsg = "Page not provided."
        print(errorMsg)
        return {"success": False, "error": errorMsg}

    try:
        # 提取函数
        async def extract_from_elements(elements):
            data = {}
            for element in elements:
                content_element = await element.querySelector('.reply-content, .reply-content-container')
                like_element = await element.querySelector('.reply-like span')

                if content_element:
                    text_content = await page.evaluate('(element) => element.innerText.trim()', content_element)
                    if like_element:
                        likes = await page.evaluate('(element) => element.innerText.trim()', like_element)
                        data[text_content] = int(likes)
                    else:
                        data[text_content] = 0
            return data

        # 从主评论容器中获取评论和点赞
        primary_elements = await page.querySelectorAll(f'.{primary_class_name}')
        primary_data = await extract_from_elements(primary_elements)

        # 从子评论容器中获取评论和点赞
        secondary_elements = await page.querySelectorAll(f'.{secondary_class_name}')
        secondary_data = await extract_from_elements(secondary_elements)

        # 合并结果
        merged_data = {**primary_data, **secondary_data}

        return {"success": True, "data": merged_data}

    except Exception as error:
        errorMsg = f"Failed to fetch comments and likes: {str(error)}"
        print(errorMsg)
        return {"success": False, "error": errorMsg}


# 找到桌面文件
def find_file_on_desktop(filename):
    os_type = platform.system()

    if os_type == "Windows":
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    elif os_type == "Darwin":  # macOS
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    else:
        raise EnvironmentError("Unsupported operating system")

    for root, dirs, files in os.walk(desktop_path):
        if filename in files:
            return os.path.join(root, filename)
    return None


# 从文件夹获取已经爬取的评论标题
def get_crawled_titles(desktop_file_name):
    # 判断文件是否为Excel文件
    if desktop_file_name.endswith(".xlsx"):
        # 使用文件名，不带扩展名，作为文件夹名的一部分
        folder_name = desktop_file_name.rsplit('.', 1)[0]
    else:
        # 使用空字符串作为默认文件夹名的一部分
        folder_name = ""

    # 创建或查找名为 "文件夹名/评论爬取结果" 的文件夹
    folder_path = os.path.join(os.path.expanduser("~"), "Desktop", folder_name, "评论爬取结果")

    titles = set()

    if not os.path.exists(folder_path):
        return titles

    for file in os.listdir(folder_path):
        if file.endswith(".csv"):
            # 提取标题
            title = file.split(' ')[1]
            title_without_csv = title.replace(".csv", "")  # 去掉.csv后缀
            titles.add(title_without_csv)
    return titles


def clean_filename(filename):
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in invalid_chars:
        filename = filename.replace(char, '_')  # 替换为下划线或其他安全字符
    return filename


def truncate_title(title, max_length=100):
    if len(title) <= max_length:
        return title
    else:
        truncated_title = title[:max_length - 3] + "..._"  # Add ellipsis to indicate truncation
        return truncated_title


def save_comments_to_desktop_folder(comments, page_title, num_comments, page_url, file_path):
    """
    保存评论到桌面上的"评论爬取结果"文件夹中并在原始Excel文件中标记URL已经被爬取。

    参数:
    - comments ({items}): 评论的列表。
    - page_title (str): 页面标题，用作文件名的一部分。
    - num_comments (int): 评论的数量，用作文件名的一部分。
    - page_url (str): 页面URL，用于在原始Excel文件中进行匹配。
    - file_path (str): 原始Excel文件路径。

    返回:
    - bool: True如果成功，False否则。
    """
    print("保存")

    # 在创建DataFrame之前修改数据
    data = []
    for comment, like_count in comments.items():
        data.append([comment, like_count, page_url])  # 添加page_url作为第三个值

    # 创建DataFrame
    df = pd.DataFrame(data, columns=['评论内容', '点赞数量', '内容链接'])

    file_name = os.path.basename(file_path)
    try:
        # 获取桌面路径
        os_type = platform.system()

        if os_type in ["Windows", "Darwin"]:
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        else:
            raise EnvironmentError("Unsupported operating system")

        # 获取原始文件夹名
        folder_name = file_name.rsplit('.', 1)[0]

        # 在桌面路径上添加 "文件夹名/评论爬取结果" 文件夹
        folder_path = os.path.join(desktop_path, folder_name, "评论爬取结果")

        # 如果 "文件夹名/评论爬取结果" 文件夹不存在，则创建它
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # 处理文件标题防止过长保存不了
        truncated_title = truncate_title(page_title, max_length=100)
        save_file_name = f"{num_comments}条 {truncated_title}.xlsx"
        comments_file_path = os.path.join(folder_path, save_file_name)

        # 格式化文件名
        try:
            df.to_excel(comments_file_path, index=False)
            print("结果已保存到:" + comments_file_path)
        except Exception as e:
            # 如果保存失败，使用格式化标题重试
            print(f"使用原始标题保存失败，原因: {e}. 尝试使用格式化标题保存...")
            safe_title = clean_filename(truncated_title)
            save_file_name = f"{num_comments}条 {safe_title}.xlsx"
            comments_file_path = os.path.join(folder_path, save_file_name)
            df.to_excel(comments_file_path, index=False)
            print("结果已保存到:" + comments_file_path)

        if not os.path.exists(file_path):
            print(f"没有发现文件: {file_name}")
            return False

        # 读取文件
        original_excel_df = pd.read_excel(file_path)

        # 寻找包含特定URL格式的列
        url_column = find_url_column(original_excel_df)

        if not url_column:
            print("URL column not found in the Excel file.")
            return False

        # 找到对应的URL，并标记为"已爬取"
        original_excel_df.loc[original_excel_df[url_column] == page_url, "是否爬取"] = "已爬取"

        # 保存回原始文件
        original_excel_df.to_excel(file_path, index=False)
        print("原始文件已更新")

        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def mark_url_as_exception_in_excel(web_url, filename):
    file_path = find_file_on_desktop(filename)
    if not file_path:
        print(f"没有发现桌面存在文件: {filename}")
        return

    # 读取文件
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return

    # 查找包含URL的列
    url_column = find_url_column(df)

    if not url_column:
        print("URL column not found in the Excel file.")
        return

    # 标记URL为“爬取异常”
    df.loc[df[url_column] == web_url, "是否爬取"] = "爬取异常"

    # 保存文件
    df.to_excel(file_path, index=False)
    print(f"已将URL {web_url} 标记为 '爬取异常'")


def get_urls_from_file(file_path):
    """
    获取评论源文件的 URL 合集。

    参数:
    - file_path (str): 文件路径。

    返回:
    - list: 包含未爬取评论合集的 URL 数组
    """
    # file_path = find_file_on_desktop(filename)

    if not file_path:
        print(f"没有发现桌面存在文件: {file_path}")
        return None, None, None, None, None

    try:
        os.chmod(file_path, 0o666)
    except Exception as e:
        print(f"Error setting file permissions for {file_path}: {e}")

    # 读取文件
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None, None, None, None, None

    # 如果没有 '是否爬取' 列，添加它
    if "是否爬取" not in df.columns:
        print("缺少 '是否爬取' 列，正在添加...")
        df["是否爬取"] = "未爬取"
        try:
            df.to_excel(file_path, index=False)  # 保存更新后的文件
            print(f"成功添加 '是否爬取' 列到 {file_path}")
        except Exception as e:
            print(f"Error saving updated file {file_path}: {e}")
            return None, None, None, None, None

    # 查找包含URL的列
    url_column = find_url_column(df)

    if not url_column:
        print("URL column not found in the Excel file.")
        return [], 0, 0, 0, 0

    # 根据"是否爬取"列过滤数据
    to_crawl_df = df[(df["是否爬取"] != "已爬取") & (df["是否爬取"] != "爬取异常")]
    crawled_df = df[df["是否爬取"] == "已爬取"]

    # 获取已爬取的标题
    # crawled_titles = get_crawled_titles(file_name)
    # crawled_titles_count = len(crawled_titles)
    # print(f"文件夹中已有的爬取标题数量: {crawled_titles_count}")

    total_comments = len(df)
    crawled_comments = len(crawled_df)
    to_crawl_comments = len(to_crawl_df)
    linkrot_comments = total_comments - crawled_comments - to_crawl_comments

    # print(f"总链接数量: {total_comments}")
    # print(f"已爬取数量: {crawled_comments}")
    # print(f"失效链接数: {linkrot_comments}")
    # print(f"待爬取数量: {to_crawl_comments}")

    return to_crawl_df[url_column].tolist(), total_comments, crawled_comments, linkrot_comments, to_crawl_comments


def find_url_column(df):
    """
    根据给定的 DataFrame 找到包含 URL 的列。

    参数:
    - df (pd.DataFrame): 输入的 DataFrame。

    返回:
    - str: 包含 URL 的列名称，如果找不到则返回 None。
    """
    for column in df.columns:
        if (df[column].astype(str).str.contains("http", case=False).any()) and (
                df[column].astype(str).str.contains("douyin|xiaohongshu|bilibili", case=False, regex=True).any()):
            return column
    return None


def update_excel_with_metrics(file_path, web_url, num_comments, num_likes, num_collections):
    """
    更新Excel文件中的评论数量、点赞数量和收藏数量。

    参数:
    - file_path (str): Excel文件的路径。
    - web_url (str): 要更新的URL。
    - num_comments (int): 评论数。
    - num_likes (int): 点赞数。
    - num_collections (int): 收藏数。

    返回:
    - bool: 更新是否成功。
    """
    try:
        # 读取文件
        df = pd.read_excel(file_path)

        # 寻找包含特定URL格式的列
        url_column = find_url_column(df)

        if not url_column:
            print("URL column not found in the Excel file.")
            return False

        # 使用正则表达式提取视频ID或内容ID
        content_id = re.search(r'(video|explore)/([\w\d]+)', web_url)

        if content_id:
            content_id = content_id.group(2)
            # 根据ID找到与给定web_url匹配的行
            url_mask = df[url_column].astype(str).str.contains(content_id, case=False)
        else:
            # 对于短链接，尝试模糊匹配
            url_mask = df[url_column].astype(str).str.contains(web_url, case=False)

        # 更新或创建“评论数”、“点赞数”和“收藏数”列
        if '评论数量' not in df.columns:
            df['评论数量'] = 0
        if '点赞数量' not in df.columns:
            df['点赞数量'] = 0
        if '收藏数量' not in df.columns:
            df['收藏数量'] = 0

        df.loc[url_mask, '评论数量'] = num_comments
        df.loc[url_mask, '点赞数量'] = num_likes
        df.loc[url_mask, '收藏数量'] = num_collections

        # 保存回原始文件
        df.to_excel(file_path, index=False)
        print("Excel文件已更新")
        return True
    except Exception as e:
        print(f"Error updating the Excel file: {e}")
        return False


# 主爬虫
async def crawl_one_url(web_url, browser, file_path):
    """
    根据给定的URL抓取评论，并保存到桌面指定文件夹。

    参数:
    - web_url (str): 要抓取的网页URL。
    - browser (pyppeteer.browser.Browser): 已经打开的浏览器实例。
    - file_path (str): 原始Excel文件的路径。

    注意:
    - 如果URL中包含 'douyin'，则不点击作者栏，直接进行按键操作。
    - 如果URL中包含 'xiaohongshu'，则先点击作者栏再进行按键操作。
    """

    file_name = os.path.basename(file_path)
    comments = []

    try:
        page, page_title = await open_and_load_url_in_new_tab(web_url, browser)
        print(f"页面标题: {page_title}")
        if not page_title:
            mark_url_as_exception_in_excel(web_url, file_name)
            print(f"URL {web_url} 有异常，页面标题为空。")
            try:
                await page.close()
            except pyppeteer.errors.NetworkError as e:
                print(f"Error closing page: {e}")
            return

        # 根据URL决定是否点击作者栏
        if "xiaohongshu" in web_url:
            click_result = await click_element_by_class(page, 'author')
            if not click_result['success']:
                print("点击作者栏失败")
                return
        elif "douyin" in web_url:
            # 如果是douyin，直接按键
            pass
        elif "bilibili" or "b23" in web_url:
            # 如果是bilibili，直接按键
            pass
        else:
            print("URL不包含 'douyin' 或 'xiaohongshu' 或 'bilibili'")
            return

        # 获取评论数量
        social_metrics = await extract_social_metrics(page, web_url)

        num_comments = social_metrics['comments']
        num_likes = social_metrics['likes']
        num_collects = social_metrics['collects']
        print("评论数量:", num_comments, "点赞数量", num_likes, "收藏数量", num_collects)
        update_excel_with_metrics(file_path, web_url, num_comments, num_likes, num_collects)

        # 调用示例
        if "xiaohongshu" in web_url:
            press_result = await press_keys(page, ['ArrowDown'], '出现某些元素',
                                            ["end-container"], 0.01)
            print(press_result)
            if not press_result['success']:
                print("按键操作失败")
                return

        elif "douyin" in web_url:
            press_result = await press_keys(page, ['Alt', 'ArrowDown'], '出现某些文字',
                                            ['暂时没有更多评论'])
            if not press_result['success']:
                print("按键操作失败")
                return
        #
        elif "bilibili" or "b23" in web_url:
            press_result = await press_keys(page, ['Alt', 'ArrowDown'], '出现某些文字',
                                            ['没有更多评论'], 0.5)
            if not press_result['success']:
                print("按键操作失败")
                return

        print("xiaohongshu")
        # 根据URL决定是否点击作者栏
        if "xiaohongshu" in web_url:
            print("xiaohongshu")
            fetch_red_book_comments_and_likes_result = await fetch_red_book_comments_and_likes(page)
            if fetch_red_book_comments_and_likes_result['success']:
                comments = fetch_red_book_comments_and_likes_result['data']
                print(comments)
            pass
        elif "douyin" in web_url:
            fetch_douyin_comments_and_likes_result = await fetch_douyin_comments_and_likes(page)
            if fetch_douyin_comments_and_likes_result['success']:
                comments = fetch_douyin_comments_and_likes_result['data']
                print(comments)
            pass
        elif "bilibili" or "b23" in web_url:
            fetch_red_book_comments_and_likes_result = await fetch_bilibili_comments_and_likes(page)
            if fetch_red_book_comments_and_likes_result['success']:
                comments = fetch_red_book_comments_and_likes_result['data']
                print(comments)

        else:
            print("URL不包含 'douyin' 或 'xiaohongshu' 或 'bilibili'")
            return

        saved_successfully = save_comments_to_desktop_folder(comments, page_title, num_comments, web_url, file_path)
        # 保存评论
        if saved_successfully:
            await asyncio.sleep(2)
    except Exception as e:
        print(f"Error: {e}")


def show_popup(title, text):
    os_type = platform.system()

    if os_type == "Windows" or os_type == "Linux":
        root = tk.Tk()
        root.withdraw()  # 隐藏主Tk窗口
        messagebox.showinfo(title, text)
        root.destroy()

    elif os_type == "Darwin":  # macOS
        applescript_command = f'''
        display dialog "{text}" with title "{title}" buttons {{"OK"}}
        '''
        subprocess.run(["osascript", "-e", applescript_command])

    else:
        print("Unsupported operating system")


def update_info_label(text):
    info_label.config(text=text)


async def process_all_urls(web_urls, file_path):
    if not await is_chrome_debugging_port_available():
        start_chrome_debugging()

    browser = await get_browser()

    print("开始爬取")
    for url in web_urls:
        print(url)
        try:
            urls, total_comments, crawled_comments, linkrot_comments, to_crawl_comments = get_urls_from_file(file_path)
            percentage = (crawled_comments) / total_comments * 100
            text = f"正在爬取第{crawled_comments + 1}条链接，共{total_comments}条链接，失效链接 {linkrot_comments} 条，处理进度: {percentage:.2f}%"
            window.after(0, update_info_label, text)
            await asyncio.wait_for(crawl_one_url(url, browser, file_path), timeout=1000000)

        except Exception as e:
            print(f"Processing {url} error!")

    urls, total_comments, crawled_comments, linkrot_comments, to_crawl_comments = get_urls_from_file(
        file_path)
    info_label.config(
        text=f"爬虫任务已完成，总共 {total_comments} 个链接，已爬取 {crawled_comments} 个，失效 {linkrot_comments} 个，待爬取 {to_crawl_comments} 个")

    run_button.config(text="爬取完成")
    print("爬取任务完成")
    # 在处理完所有任务后关闭浏览器
    await browser.close()
    return True


check = False


def run_script():
    selected_file = selected_file_button["text"]
    if selected_file and check:
        urls, total_comments, crawled_comments, linkrot_comments, to_crawl_comments = get_urls_from_file(selected_file)
        if len(urls):
            thread = threading.Thread(target=asyncio.run, args=(process_all_urls(urls, selected_file),))
            thread.start()
        else:
            urls, total_comments, crawled_comments, linkrot_comments, to_crawl_comments = get_urls_from_file(
                selected_file)
            info_label.config(
                text=f"爬虫任务已完成，总共 {total_comments} 个链接，已爬取 {crawled_comments} 个，失效 {linkrot_comments} 个，待爬取 {to_crawl_comments} 个")
    else:
        info_label.config(text=f"请选择正确包含链接列的 Excel 文件")


def browse_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        selected_file_button["text"] = file_path
        check_excel_file(file_path)


def check_excel_file(file_path):
    global check
    _, file_extension = os.path.splitext(file_path)
    if file_extension.lower() in ['.xlsx', '.xls']:
        info_label.config(text="选中的文件是Excel文件")
        check = True
        selected_file = selected_file_button["text"]
        if selected_file:
            urls, total_comments, crawled_comments, linkrot_comments, to_crawl_comments = get_urls_from_file(
                selected_file)
            info_label.config(
                text=f"一共找到 {total_comments} 条链接，已爬取 {crawled_comments} 个，失效 {linkrot_comments} 个,待爬取 {to_crawl_comments} 个")

    else:
        info_label.config(text="选中的文件不是Excel文件")
        check = False


asyncio.run(is_chrome_debugging_port_available())
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

run_button = tk.Button(window, text="启动爬虫脚本", command=run_script)
run_button.pack(pady=10)  # 添加垂直内边距

# 运行主循环
window.mainloop()
