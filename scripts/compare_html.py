from bs4 import BeautifulSoup
from mitmproxy import io, http
from mitmproxy import ctx
from mitmproxy import connections
from diff_match_patch import diff_match_patch
import difflib
from pprint import pprint
import sys
import json
class FlowComparator:
	def __init__(self):
		self.cnt = 0

	def diff_content(self, first_content, second_content):
		first_soup = BeautifulSoup(first_content.response.content, "html.parser")
		second_soup = BeautifulSoup(second_content.response.content, "html.parser")
		dmp = diff_match_patch()
		patches = dmp.patch_make(str(first_soup.prettify()), str(second_soup.prettify()))
		diff = dmp.patch_toText(patches)
		if len(str(diff)) != 0:
			file = open("secClaim/1.3.3/diff_" + str(self.cnt) + ".html", "w")
			file.write(first_content.request.path + "\n")
			file.write(diff)
			file.close()		
			first_token_dict = scrape_response_for_verification_token(first_content.response.content)
			second_token_dict = scrape_response_for_verification_token(second_content.response.content)
			print(first_token_dict)
			print(second_token_dict)
			file = open("secClaim/1.3.3/diff_" + str(self.cnt) + ".html", "r")
			flag = False
			for line in file:
				token = line[1:len(line)-1]
				if line[0] == "-":
					if not check_tokens(first_token_dict, token):
						first_basket_dict = scrape_basket_items(first_content.response.content)
						if not check_tokens(first_basket_dict, token):
							print("ALAAAARM!!!!!! " + str(self.cnt))
							f = open("secClaim/1.3.3/alarm" + str(self.cnt), "w")
							f.write(first_content.request.path + "\n")
							f.write(str(first_basket_dict) + "\n")
							f.write(str(first_token_dict) + "\n")
							f.close()
				elif line[0] == "+":
					if not check_tokens(second_token_dict, token):
						second_basket_dict = scrape_basket_items(second_content.response.content)
						if not check_tokens(second_basket_dict, token):
							print("ALAAAARM!!!!!! "+ str(self.cnt))
							f = open("secClaim/1.3.3/alarm" + str(self.cnt), "w")
							f.write(second_content.request.path + "\n")
							f.write(str(second_basket_dict) + "\n")
							f.write(str(second_token_dict) + "\n")
							f.close()
				else :
					continue					
		file_one = open("secClaim/1.3.3/first_html_" + str(self.cnt) + ".html", "w")
		file_two = open("secClaim/1.3.3/second_html_" + str(self.cnt) + ".html", "w")
		self.cnt +=1
		file_one.write(str(first_soup.prettify()))
		file_two.write(str(second_soup.prettify()))
		file_one.close()
		file_two.close()
	def colour_api_diff(self, first_content, second_content):
		first_soup = BeautifulSoup(first_content.response.content, "html.parser")
		second_soup = BeautifulSoup(second_content.response.content, "html.parser")
		dmp = diff_match_patch()
		patches = dmp.patch_make(str(first_soup.prettify()), str(second_soup.prettify()))
		diff = dmp.patch_toText(patches)
		if len(diff) > 0:
			file = open("colour_diff" + str(self.cnt), "w")
			file.write(first_content.request.path + "\n")
			file.write(diff)
			if "json" in first_content.response.headers["Content-Type"]:
				newDictionary=json.loads(str(first_soup))
				has_id = False
				has_colour_name = False
				if isinstance(newDictionary, dict):
					has_id = check_id(newDictionary)
					has_colour_name = check_colour_name(newDictionary)
				else:
					for dictionary in newDictionary:
						if not has_id:
							has_id = check_id(dictionary)
						if not has_colour_name:
							has_colour_name = check_colour_name(dictionary)
				if not has_id or not has_colour_name:
					print("ALAAAARM!!!!!!")
		self.cnt +=1
def check_id(dictionary):
	has_id = False
	for k,v in dictionary.items():
		if k =="id":
			has_id = True
	return has_id
def check_colour_name(dictionary):
	has_colour_name = False
	for k,v in dictionary.items():
		print(v)
		if k == "colourName":
			has_colour_name = True
	return has_colour_name
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
def check_tokens(token_dict, token):
	in_dict = False
	for k,v in token_dict.items():
		if token in v:
			in_dict = True
			break
	if not in_dict:
		return False
	return True
def scrape_basket_items(content):
    soup = BeautifulSoup(content, 'html.parser')
    input_tags = soup.find_all('input')
    items_dict = {}
    for tag in input_tags:
        if 'name' in tag.attrs:
            if 'Items' in tag['name']:
                items_dict[tag['name']] = tag['value']
    print("Stvorio sam " + str(items_dict))
    return items_dict