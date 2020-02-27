import random
import sys
from mitmproxy import io, http
import typing  # noqa
import requests 


class Writer:
    def __init__(self, path: str) -> None:
        self.f: typing.IO[bytes] = open(path, "wb")
        self.w = io.FlowWriter(self.f)

    def response(self, flow: http.HTTPFlow) -> None:
        self.w.add(flow)

    def request(self, flow: http.HTTPFlow) -> None:
    	self.w.add(flow)
    	f = open('out1.txt', 'w')
    	r = requests.get('http://192.168.8.101:5000')
    	f.write(str(r.text) + '\n')
    	f.write('-----------------------\n')
    	f.write(str(r.cookies) + '\n')
    	f.write('-----------------------\n')
    	f.write(str(r.headers) + '\n')
    	f.write('-------------------------\n')
    	f.write(str(r.content) + '\n')
    	f.write('----------------------------\n')
    	data = r.request.headers
    	f.write("Request info\n")
    	f.write(str(data) + '\n')
    	f.write('---------------------------\n')
    	f.close()
    
    def done(self):
        self.f.close()


addons = [Writer('out.txt')]