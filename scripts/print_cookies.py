import random
import sys
from mitmproxy import io, http
import typing  # noqa
import requests 
from mitmproxy import ctx
from mitmproxy import connections
class Writer:
    def __init__(self):
        self.f1 = open('cookies-app-1.txt', "w")
        self.f2 = open('cookies-app-2.txt', 'w')
        self.f3 = open('app-1-request-headers.txt', 'w')
        self.f4 = open('app-2-request-headers.txt', 'w')
        self.f5 = open('app-1-reponse-headers.txt', 'w')
        self.f6 = open('app-2-response-headers.txt', 'w')
    def response(self, flow: http.HTTPFlow) -> None:
        response_headers = {}
        for k, v in flow.response.headers.items():
            response_headers[k] = v
        self.f5.write(str(response_headers))

    def request(self, flow: http.HTTPFlow) -> None:
        request_headers = {}
        for k, v in flow.request.headers.items():
            request_headers[k] = v
        self.f1.write(str(flow.request.headers.get_all("Cookie")) + '\n')
        flow1 = flow.copy()
        flow1.request.port = 5000
        r = requests.get(flow1.request.url)
        self.f2.write(str(r.headers['set-cookie']) + '\n')
        self.f3.write(str(request_headers) + '\n')
        self.f4.write(str(r.request.headers) + '\n')
        self.f6.write(str(r.headers) + '\n')
    
    def done(self):
        self.f1.close()
        self.f2.close()   
        self.f3.close()
        self.f4.close()
        self.f5.close()
        self.f6.close() 
addons = [Writer()]