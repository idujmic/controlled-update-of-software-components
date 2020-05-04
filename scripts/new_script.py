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
	def __init__(self, legal_diffs, port, tokens_for_scraping, host, path):
		self.cmp = FlowComparator(legal_diffs, path)
		self.token_dict = {}
		self.cookie = ""
		self.flows_dict = {}
		self.host = host
		print(self.host)
		self.port = port
		self.tokens_for_scraping = tokens_for_scraping
		self.waiting_dictionary = {}
		self.repeating_path_requests_dictionary = {}
	def response(self, flow: http.HTTPFlow) -> None:
		if "png" not in str(flow.request.path) and "avg" not in str(flow.request.path) and "images" not in str(flow.request.path):
			if str(self.host) == str(flow.request.host):
				self.flows_dict[flow.request.path][flow.request.headers["ordering_number"]].put(flow)
		if flow.request.port == self.port:
			if "Set-Cookie" in flow.response.headers:
				splitted_cookie = flow.response.headers["Set-Cookie"].split(";")
				self.cookie = splitted_cookie[0] + ";" + self.cookie
			if flow.request.method.lower() == "get":
				if "Content-Type" in flow.response.headers:
					if "html" in flow.response.headers["Content-Type"]:
						token_dict, has_token = scrape_response_for_tokens(flow.response.content, self.tokens_for_scraping)
						if has_token:
							self.token_dict = token_dict
			if "logout" in flow.request.path.lower() and flow.request.method.lower() == "post":
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
				if "Content-Type" in flow.request.headers:
					if "json" not in flow.request.headers["Content-Type"]:
						body_dict = split_body(request_body)
						for k1,v1 in body_dict.items():
							for k2,v2 in self.token_dict.items():
								k1_compared = k1
								if "%" in k1:
									k1_compared = urllib.parse.unquote(k1)
								if k2 in k1_compared:
										body_dict[k1] = v2
						body = build_body(body_dict)
						body = gzip.compress(bytes(body, 'utf-8'))
						flow_copy.request.content = gzip.decompress(body)
		if 'Cookie' in flow.request.headers:
			flow_copy.request.headers["Cookie"] = self.cookie
		if "view" in ctx.master.addons:
			ctx.master.commands.call("view.flows.add", [flow_copy])
		if ".png" not in str(flow.request.path) and ".avg" not in str(flow.request.path) and "images" not in str(flow.request.path):
			if not flow.request.path in self.flows_dict:
				self.repeating_path_requests_dictionary[flow.request.path] = 1
				q = queue.Queue()
				flow.request.headers["ordering_number"] = str(self.repeating_path_requests_dictionary[flow.request.path])				
				flow_copy.request.headers["ordering_number"] =str(self.repeating_path_requests_dictionary[flow.request.path])				
				self.flows_dict[flow.request.path] = {}
				self.flows_dict[flow.request.path][str(self.repeating_path_requests_dictionary[flow.request.path])] = q
				self.repeating_path_requests_dictionary[flow.request.path] += 1
			else:
				flow.request.headers["ordering_number"] = str(self.repeating_path_requests_dictionary[flow.request.path])				
				flow_copy.request.headers["ordering_number"] =str(self.repeating_path_requests_dictionary[flow.request.path])	
				q = queue.Queue()
				self.flows_dict[flow.request.path][str(self.repeating_path_requests_dictionary[flow.request.path])] = q
				self.repeating_path_requests_dictionary[flow.request.path] += 1

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
	return token_dict, bool(token_dict)				
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
	print(argument)
	threading.Timer(45.0, checker, [argument]).start()
	waiting_list = []
	for k1,v1 in argument[0].flows_dict.items():
		for k2,v2 in v1.items():
			if v2.qsize() < 2:
				wait = {}
				wait[k1] = k2
				waiting_list.append(wait)
				continue
			a = v2.get()
			b = v2.get()
			argument[0].cmp.diff_content(a,b)
	cnt = 0
	while cnt < len(waiting_list):
		for wait in waiting_list:
			for k,v in wait.items():
				if argument[0].flows_dict[k][v].qsize() == 2:
					a = argument[0].flows_dict[k][v].get()
					b = argument[0].flows_dict[k][v].get()
					argument[0].cmp.diff_content(a,b)
					cnt +=1
def read_config_file(path):
	config_file = open(path, "r")
	legal_diffs = []
	tokens_for_scraping = []
	for line in config_file:
		if line[0] == ":":
			token = line[1:].rstrip()
			legal_diffs.append(token)
		elif line[0] == "+":
			token = line[1:].rstrip()
			tokens_for_scraping.append(token)
		else:
			continue
	config_file.close()
	return legal_diffs, tokens_for_scraping
legal_diffs,tokens_for_scraping = read_config_file("odoo_config.txt")
print(legal_diffs)
print(tokens_for_scraping)
addons = [Writer(legal_diffs, 8070, tokens_for_scraping, "localhost", "odoo/test_v6/")]
#addons = [Writer(["id"], 9000, [])]
checker(addons)