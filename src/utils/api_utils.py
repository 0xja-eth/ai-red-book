from src.core.publisher import Platform
from src.utils.request_utils import request

def login(name: str, platform: Platform, cookies: list, stat: dict = None):
    """
    登陆
    :param name: 账号名
    :param platform: 平台（"xhs", "dy", "wx"）
    :param cookies: cookies
    :param stat: 统计信息
    :return: 用户信息，key（登陆凭证）
    """
    res = request.post('/api/redbook/login', {
        'name': name, 'platform': platform, 'cookies': cookies, 'stat': stat
    })
    request.set_header('Authorization', res["key"])
    return res


def generate(generation: dict):
    """
    生成
    :param generation: 生成内容
    :return: 生成结果
    """
    return request.post('/api/redbook/generate', {'generation': generation})


def publish(publication: dict):
    """
    生成
    :param publication: 发布内容
    :return: 发布结果
    """
    return request.post('/api/redbook/publish', {'publication': publication})
