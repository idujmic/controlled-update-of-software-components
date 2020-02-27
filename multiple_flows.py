import random
import sys
from mitmproxy import io, http
import typing  # noqa
import requests 
from mitmproxy import ctx
from mitmproxy import connections

class Writer:
    def __init__(self, path: str) -> None:
        self.f: typing.IO[bytes] = open('out2.txt', "wb")
        self.w = io.FlowWriter(self.f)
        self.f1: typing.IO[bytes] = open('out1.txt', "wb")
        self.w1 = io.FlowWriter(self.f1)
        self.f2 = open('cookie1.txt', "w")
        self.f3 = open('cookie2.txt', "w")
        self.flag = True


    def response(self, flow: http.HTTPFlow) -> None:
        if flow.request.port == 5106:
            self.w.add(flow)
            self.w.add(flow.response)
            self.f2.write(str(flow.request.cookies) + '\n')
        elif flow.request.port == 5000:
            self.w1.add(flow)
            self.w1.add(flow.response)
            self.f3.write(str(flow.request.cookies) + '\n')

    def request(self, flow: http.HTTPFlow) -> None:
        if flow.request.is_replay:
            return
        self.f2.write(str(flow.request.headers.get_all("Cookie"))) 
        print(flow.request.headers.get_all("Cookie")[0])
        flow1 = flow.copy()
        flow1.request.port = 5000
        if self.flag:
            r = requests.get(flow1.request.url)
            print(r.request.headers)
            print(r.headers)
            for cookie in r.cookies:
                print(str(cookie))
        try:
            req = http.HTTPRequest.make(str(flow1.request.method).upper(), str(flow1.request.url))
        except ValueError as e:
            raise exceptions.CommandError("Invalid URL: %s" % e)
        c = connections.ClientConnection.make_dummy(("", 0))
        s = connections.ServerConnection.make_dummy((req.host, req.port))
        f4 = http.HTTPFlow(c, s)
        f4.request = req
        f4.request.headers["Host"] = req.host
        f4.request.headers['cookie'] = flow.request.headers.get_all("Cookie")[0]
        print(f4.request.headers.get_all("Cookie")[0])
        #ctx.master.commands.call("replay.client", [f4])
        self.w1.add(f4)
        self.f3.write(str(f4.request.cookies) + '\n')
    
    def done(self):
        self.f.close()
        self.f1.close()
        self.f2.close()
        self.f3.close()

addons = [Writer('out.txt')]