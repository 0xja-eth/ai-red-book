
import requests, json

from src.config import config_loader

class Request:

  host = ""
  headers = {'Content-Type': 'application/json'}

  def __init__(self, host):
    self.host = host

  def set_header(self, key, value):
    self.headers[key] = value

  def get(self, route, data):
    url = "%s/%s" % (self.host, route)
    return requests.get(url, headers=self.headers, data=json.dumps(data)).json()

  def post(self, route, data):
    url = "%s/%s" % (self.host, route)
    return requests.post(url, headers=self.headers, data=json.dumps(data)).json()

backend_url = config_loader.get('Common', 'backend_url')

# 可以理解为全局单例，使用该对象进行请求，比如：
#
# import request from request_utils
#
# login_res = request.post('/api/redbook/login', login_params)
# request.set_header('Authorization', login_res["key"])
# request.post('/api/redbook/generate', generate_params)
request = Request(backend_url)

