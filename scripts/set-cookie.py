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
class Writer:
    def __init__(self):
        self.request_flag = True
        self.response_flag = True
        self.first_get_flag = True
        self.cookie = []
        self.f1 = open('new-cookie.txt', 'w')
        self.f2: typing.IO[bytes] = open('app-2-response.txt', "wb")
        self.w1 = io.FlowWriter(self.f2)    
        self.f3: typing.IO[bytes] = open('app-1-response.txt', 'wb')
        self.w2 = io.FlowWriter(self.f3)
        self.f4: typing.IO[bytes] = open('junk.txt', 'wb')
        self.w3 = io.FlowWriter(self.f4)
        self.f5: typing.IO[bytes] = open('first-get.html', 'wb')
        self.w4 = io.FlowWriter(self.f5)
        self.token_dict = {}
        self.items_dict = {}
        self.basket_verification = {}

    def response(self, flow: http.HTTPFlow) -> None:
        if self.response_flag:
            self.response_flag = False
            self.w3.add(flow)
        elif flow.request.port == 5106:
            self.w2.add(flow)
        elif flow.request.port == 5000:
            if self.first_get_flag:
                self.w4.add(flow)
                self.first_get_flag = False
                self.token_dict = scrape_response_for_verification_token(flow.response.content)
            for k, v in flow.response.headers.items():
                if k == 'Set-Cookie':
                    line = v.split(';')
                    self.cookie[0] = line[0] + '; ' + self.cookie[0] 
            if str(flow.request.method).lower() == 'get' and str(flow.request.path).lower() == '/basket':
                self.items_dict = scrape_basket_items(flow.response.content)
                self.basket_verification = scrape_basket_verification(flow.response.content)
            self.w1.add(flow)

    def request(self, flow: http.HTTPFlow) -> None:
        if flow.request.is_replay:
            return
        flow1 = flow.copy()
        flow1.request.port = 5000
        if self.request_flag:
            r = requests.get(flow1.request.url)
            self.cookie = [str(r.headers['set-cookie'])]
            self.request_flag = False
        else:
            flow1.request.headers['Host'] = str(flow1.request.host) + ':' + str(flow1.request.port)
            flow1.request.headers['Referer'] = 'http://' + str(flow1.request.host) + ':' + str(flow1.request.port) + '/'
            if 'Origin' in flow1.request.headers:
                flow1.request.headers['Origin'] = 'http://' + flow1.request.headers['Host']
            if str(flow1.request.method).lower() == 'post' and str(flow1.request.path).lower() == '/basket':
                body_dict = split_body(flow1.request.get_text())
                body_dict['__RequestVerificationToken'] = self.token_dict[body_dict['id']]
                body = build_body(body_dict)
                body = gzip.compress(bytes(body, 'utf-8'))
                flow1.request.content = gzip.decompress(body)
            if str(flow1.request.path).lower() == '/basket/update' and str(flow1.request.method).lower() == 'post':
                update_body = build_update_body(self.items_dict, self.basket_verification)
                update_body = gzip.compress(bytes(update_body, 'utf-8'))
                flow1.request.content = gzip.decompress(update_body)
            flow1.request.headers['Cookie'] = self.cookie[0]
            if "view" in ctx.master.addons:
                ctx.master.commands.call("view.flows.add", [flow1])
            ctx.master.commands.call("replay.client", [flow1])
    def done(self):
        self.f1.close()
        self.f2.close()
        self.f3.close()
        self.f4.close()
        self.f5.close()

def split_body(body):
    body_dictionary = {}
    first_split = body.split("&")
    for item in first_split:
        line = item.split("=")
        body_dictionary[line[0]] = line[1]
    return body_dictionary
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
def build_update_body(basket_items, basket_verification):
    temp = []
    body = ''
    for k, v in basket_items.items():
        item = k + '=' + v
        temp.append(item)
    temp.append('updatebutton=')
    for k, v in basket_verification.items():
        item = k + '=' + v
        temp.append(item)
    size = len(temp)
    for i in range(0, size - 1):
        body += temp[i] + '&'
    body += temp[size-1]
    return body

def scrape_response_for_verification_token(content):
    soup = BeautifulSoup(content, 'html.parser')
    input_tags = soup.find_all('input')
    cnt = 1
    token_dict = {}
    for tag in input_tags:
        if 'name' in tag.attrs:
            if tag['name'] == '__RequestVerificationToken':
                token_dict[str(cnt)] = tag['value']
                cnt +=1
    return token_dict
def scrape_basket_items(content):
    soup = BeautifulSoup(content, 'html.parser')
    input_tags = soup.find_all('input')
    items_dict = {}
    for tag in input_tags:
        if 'name' in tag.attrs:
            if 'Items' in tag['name']:
                items_dict[tag['name']] = tag['value']
    return items_dict
def scrape_basket_verification(content):
    soup = BeautifulSoup(content, 'html.parser')
    input_tags = soup.find_all('input')
    basket_verification = {}
    for tag in input_tags:
        if 'name' in tag.attrs:
            if tag['name'] == '__RequestVerificationToken':
                basket_verification[tag['name']] = tag['value']
    return basket_verification
addons = [Writer()]