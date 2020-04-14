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
import queue
import threading
from new_compare import *
import urllib.parse

class Writer:
	def __init__(self, legal_diffs, port, tokens_for_scraping):
		self.cmp = FlowComparator(legal_diffs)
		self.token_dict = {}
		self.cookie = ""
		self.flows_dict = {}
		self.host = get_ip_address()
		print(self.host)
		self.port = port
		self.tokens_for_scraping = tokens_for_scraping
	def response(self, flow: http.HTTPFlow) -> None:
		if "png" not in str(flow.request.path) and "avg" not in str(flow.request.path) and "images" not in str(flow.request.path):
			if str(self.host) == str(flow.request.host):
				print("Dodajem "+ str(flow.request.path))
				self.flows_dict[flow.request.path].put(flow)
				print(self.flows_dict)
		if flow.request.port == self.port:
			if "Set-Cookie" in flow.response.headers:
				splitted_cookie = flow.response.headers["Set-Cookie"].split(";")
				self.cookie = splitted_cookie[0] + ";" + self.cookie
			if flow.request.method.lower() == "get":
				if "Content-Type" in flow.response.headers:
					if "html" in flow.response.headers["Content-Type"]:
						self.token_dict = scrape_response_for_tokens(flow.response.content, self.tokens_for_scraping)
			if "logout" in flow.request.path.lower() and flow.request.method.lower() == "post":
				print("Praznim cookie")
				self.cookie = ""
	def request(self, flow: http.HTTPFlow) -> None:
		if flow.request.is_replay:
			return
		if str(self.host) != str(flow.request.host):
			return
		flow_copy = flow.copy()
		flow_copy.request.port = self.port
		if flow.request.method.lower() == 'post':
			request_body = flow.request.get_text()
			if len(request_body) > 0:
				body_dict = split_body(request_body)
				print(body_dict)
				print(self.token_dict)
				for k1,v1 in body_dict.items():
					for k2,v2 in self.token_dict.items():
						k1_compared = k1
						if "%" in k1:
							k1_compared = urllib.parse.unquote(k1)
							print(k1_compared)
						if k2 in k1_compared:
								body_dict[k1] = v2
				print(body_dict)
				body = build_body(body_dict)
				body = gzip.compress(bytes(body, 'utf-8'))
				flow_copy.request.content = gzip.decompress(body)
		if 'Cookie' in flow.request.headers:
			flow_copy.request.headers["Cookie"] = self.cookie
		if "view" in ctx.master.addons:
			ctx.master.commands.call("view.flows.add", [flow_copy])
		if ".png" not in str(flow.request.path) and ".avg" not in str(flow.request.path) and "images" not in str(flow.request.path):
			if not flow.request.path in self.flows_dict:
				q = queue.Queue()
				self.flows_dict[str(flow.request.path)] = q
		ctx.master.commands.call("replay.client", [flow_copy])
def scrape_response_for_tokens(response, tokens):
	soup = BeautifulSoup(response, "html.parser")
	tag_list = [tag.name for tag in soup.find_all()]
	tag_set = set(tag_list)
	token_dict = {}
	for tag in tag_set:
		all_tags = soup.find_all(tag)
		for t in all_tags:
			for k,v in t.attrs.items():
				for token in tokens:
					if token in v:
						token_dict[v] = t.attrs["value"]
	return token_dict			
def split_body(body):
	body_dictionary = {}
	first_split = body.split("&")
	for item in first_split:
		line = item.split("=")
		body_dictionary[line[0]] = line[1]
	return body_dictionary
def get_ip_address():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("8.8.8.8", 80))
	return s.getsockname()[0]
def build_body(body_dictionary):
	temp = []
	body = ''
	for k, v in body_dictionary.items():
		item = k + '=' + v
		temp.append(item)
	size = len(temp)
	for i in range(0, size-1):
		body+= temp[i] + '&'
	body += temp[size-1]
	return body
def checker(argument):
	print("unutra sam")
	print(argument)
	threading.Timer(10.0, checker, [argument]).start()
	for k,v in argument[0].flows_dict.items():
		if v.qsize() % 2 == 0  and v.qsize() > 0:
			print("Usporedujem " + str(k))
			a = v.get()
			b = v.get()
			argument[0].cmp.diff_content(a,b)
addons = [Writer(["RequestVerificationToken", "Items"], 5000, ["RequestVerificationToken", "Items"])]
checker(addons)