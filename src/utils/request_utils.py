class Request:

    host = ""
    headers = {'Content-Type': 'application/json'}

    def __init__(self, host):
        self.host = host

    def set_header(self, key, value):
        self.headers[key] = value

    def request(self, route, data):
        url = "%s/%s" % (self.host, route)
        return requests.post(url, headers=self.headers, data=json.dumps(data))