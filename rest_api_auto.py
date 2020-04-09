import random
import sys
from mitmproxy import io, http
import typing  # noqa
import requests 
from mitmproxy import ctx
from mitmproxy import connections
import gzip
from bs4 import BeautifulSoup
import time
import socket
from new_compare import *
import queue
import threading
import requests
request_dict = {}
class Writer():
	def __init__(self):
		self.host = get_ip_adress()
		print(self.host)
		self.flows_dict = {}
		self.cmp = FlowComparator([])
	def response(self, flow: http.HTTPFlow) -> None:
		self.flows_dict[flow.request.path].put(flow)
	def request(self, flow:http.HTTPFlow) -> None:
		if flow.request.is_replay:
			return
		if str(self.host) != str(flow.request.host):
			print("Odbijam slanje zahtjeva")
			return
		flow1 = flow.copy()
		flow1.request.port = 9000
		if "view" in ctx.master.addons:
			ctx.master.commands.call("view.flows.add", [flow1])
		q = queue.Queue()
		self.flows_dict[flow.request.path] = q
		ctx.master.commands.call("replay.client", [flow1])
def get_ip_adress():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]
def checker(argument):
    threading.Timer(20.0, checker, [argument]).start()
    for k,v in argument[0].flows_dict.items():
        if v.qsize() == 2:
            a = v.get()
            b = v.get()
            argument[0].cmp.colour_api_diff(a,b)

addons = [Writer()]
checker(addons)