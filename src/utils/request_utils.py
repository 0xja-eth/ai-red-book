import requests, json

from src.config import config_loader


class Request:
    host = ""
    headers = {'Content-Type': 'application/json'}
    return_raw = False

    def __init__(self, host, return_raw=False):
        self.host = host
        self.return_raw = return_raw

    def set_header(self, key, value):
        self.headers[key] = value

    def _request(self, method, route, data):
        url = "%s/%s" % (self.host, route)
        print("[request] Start %s %s %s" % (method, url, data))
        response = requests.request(method, url, headers=self.headers, data=json.dumps(data))
        res_json = response.json()

        if self.return_raw:
            print("[request] End %s" % res_json)
            return res_json

        if res_json["code"] != 200:
            print("[request] Failed %s" % res_json)
            raise Exception(res_json["reason"])

        print("[request] End %s" % res_json["payload"])
        return res_json["payload"]

    def get(self, route, data):
        return self._request("GET", route, data)

    def post(self, route, data):
        return self._request("POST", route, data)

    def delete(self, route, data):
        return self._request("DELETE", route, data)

    def put(self, route, data):
        return self._request("PUT", route, data)


backend_url = config_loader.get('Common', 'backend_url')

# 可以理解为全局单例，使用该对象进行请求，比如：
#
# import request from request_utils
#
# login_res = request.post('/api/redbook/login', login_params)
# request.set_header('Authorization', login_res["key"])
# request.post('/api/redbook/generate', generate_params)
request = Request(backend_url)
