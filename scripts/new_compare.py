from bs4 import BeautifulSoup
from diff_match_patch import diff_match_patch
import sys
import json
import urllib.parse
import ast
import os.path
from os import path
class FlowComparator:
	def __init__(self, legal_diffs, path):
		self.cnt = 0
		self.legal_diffs = legal_diffs
		self.path = path
	def diff_content(self, first_flow, second_flow):
		if "Content-Type" in first_flow.response.headers:				
			if "json" in first_flow.response.headers["Content-Type"]:
				self.diff_json(first_flow, second_flow)
			else: 
				self.diff_html(first_flow, second_flow)
	def diff_html(self, first_flow, second_flow):
		first_soup = BeautifulSoup(first_flow.response.content, "html.parser")
		second_soup = BeautifulSoup(second_flow.response.content, "html.parser")
		file_one = open(self.path + "first_html_" + str(self.cnt) + ".html", "w")
		file_two = open(self.path + "second_html_" + str(self.cnt) + ".html", "w")
		file_one.write(self.path + "\n")
		file_two.write(self.path + "\n")
		file_one.write(str(first_soup.prettify()))
		file_two.write(str(second_soup.prettify()))
		file_one.close()
		file_two.close()
		file_one = open(self.path + "first_html_" + str(self.cnt) + ".html", "r")
		file_two = open(self.path + "second_html_" + str(self.cnt) + ".html", "r")
		first_soup = BeautifulSoup(file_one, "html.parser")
		second_soup = BeautifulSoup(file_two, "html.parser")
		dmp = diff_match_patch()
		patches = dmp.patch_make(str(first_soup.prettify()), str(second_soup.prettify()))
		diff = dmp.patch_toText(patches)
		if len(str(diff)) != 0:
			file = open(self.path + "diff_" + str(self.cnt), "w")
			file.write(first_flow.request.path + "\n")
			file.write(diff)
			file.close()
			first_diff_tags, second_diff_tags = get_legal_diffs_from_response(first_soup, second_soup, self.legal_diffs)
			file = open(self.path + "diff_" + str(self.cnt), "r")
			for line in file:
				token = line[1:len(line)-1]
				if "%" in token:
					token = urllib.parse.unquote(token)
				if line[0] == "-":
					if not check_tags_for_token(first_diff_tags, token):
						write_alarm_file(first_flow, diff, token, self.cnt, self.legal_diffs, self.path)
				elif line[0] == "+":
					if not check_tags_for_token(second_diff_tags, token):
						write_alarm_file(second_flow, diff, token, self.cnt, self.legal_diffs, self.path)
				else:
					continue
			file.close()

		file_one.close()
		file_two.close()
		self.cnt+=1
	def diff_json(self, first_content, second_content):
		first_soup = BeautifulSoup(first_content.response.content, "html.parser")
		second_soup = BeautifulSoup(second_content.response.content, "html.parser")
		dmp = diff_match_patch()
		patches = dmp.patch_make(str(first_soup.prettify()), str(second_soup.prettify()))
		diff = dmp.patch_toText(patches)
		file_one = open(self.path + "first_json_" + str(self.cnt) + ".json", "w")
		file_two = open(self.path + "second_json_" + str(self.cnt) + ".json", "w")
		file_one.write(str(first_content.request.path) + "\n")
		file_two.write(str(second_content.request.path) + "\n")
		file_one.write(str(first_soup.prettify()))
		file_two.write(str(second_soup.prettify()))
		file_one.close()
		file_two.close()
		first_json_dict = json.loads(first_content.response.get_text())
		second_json_dict = json.loads(second_content.response.get_text())
		json_compare(first_json_dict, second_json_dict, self.path, self.cnt)
		if path.exists(self.path + "json_diff" + str(self.cnt)):
			file = open(self.path + "json_diff" + str(self.cnt))
			tokens = []
			for line in file:
				if line[0] == "-":
					token = line[1:].split("=")[0]
					tokens.append(token)
				else:
					continue
			legal = False
			illegal_tokens = []
			for token in tokens:
				for diff in self.legal_diffs:
					if diff in token:
						legal = True
			if not legal:
				write_alarm_file(first_content, tokens, tokns, self.cnt, self.legal_diffs, self.path)
					

			#file = open("odoo/test_v1/json_diff" + str(self.cnt), "w")
			#file.write(first_content.request.path + "\n")
			#file.write(diff)
			#file.close()
			#file = open("odoo/test_v1/json_diff" + str(self.cnt), "r")
			#for line in file:
			#	token = line[1:len(line)-1]
			#	if line[0] == "-":
			#		check_json_alarm(first_json_dict, token, self.legal_diffs, diff, self.cnt, first_content)
			#	elif line[1] == "+":
			#		check_json_alarm(second_json_dict, token, self.legal_diffs, diff, self.cnt, second_content)
			#	else:
			#		continue
			#file.close()
		file_one.close()
		file_two.close()
		self.cnt +=1

def json_compare(first_json_dict, second_json_dict, path, cnt):
	diffs = []
	if first_json_dict != second_json_dict:
		file = open(path + "json_diff" + str(cnt), "w")
		if first_json_dict.keys() == second_json_dict.keys():
			file.write("JSON objekti imaju iste ključeve\n")
		else:
			first_key_diff = first_json_dict.keys() - second_json_dict
			second_key_diff = second_json_dict.keys() - first_json_dict
			file.write("JSON objekt prve aplikacije ima različite ključeve: " + str(first_key_diff)+ "\n drugi ima: " + str(second_key_diff) + "\n")
		iterate_dict(first_json_dict, second_json_dict, file, cnt)
		file.close()
def iterate_dict(first_dict, second_dict, file, cnt):
	for k1,v1 in first_dict.items():
		for k2,v2 in second_dict.items():
			if k1 == k2:
				if v1 != v2:
					if isinstance(v1,dict) and isinstance(v2,dict):
						iterate_dict(v1,v2,file, cnt)
					elif isinstance(v1, list) and (v2, list):
						if len(v1) > 0 and len(v2) > 0:
							if isinstance(v1[0], dict) and isinstance(v2[0], dict):
								for value1, value2 in zip(v1,v2):
									iterate_dict(value1, value2, file, cnt)
					else:
						file.write("-"  + str(k1) + "=" + str(v1) + "\n+" + str(k2) + "=" + str(v2) + "\n")
def check_json_alarm(json_dict, token, legal_diffs, diff, cnt, flow):
	flag = False
	if isinstance(json_dict, dict):
		if not check_json_for_token(token, json_dict, legal_diffs):
			write_alarm_file(flow, diff, token, cnt, legal_diffs)
			return
	else:
		for dictionary in json_dict:
			flag = check_json_for_token(token, dictionary, legal_diffs)
			if flag:
				break
		if not flag:
			write_alarm_file(flow, diff, token, cnt, legal_diffs)
def check_json_for_token(token, json_dict, legal_diffs):
	for k,v in json_dict.items():
		for legal_diff in legal_diffs:
			if legal_diff in str(k) and token in str(v):
				return True
			elif legal_diff in str(v) and token in str(k):
				return True
	return False
def get_legal_diffs_from_response(first_soup, second_soup, legal_diffs):
	legal_diffs_dict = {}
	first_tag_list = [tag.name for tag in first_soup.find_all()]
	second_tag_list = [tag.name for tag in second_soup.find_all()]
	first_tag_set = set(first_tag_list)
	second_tag_set = set(second_tag_list)
	first_diffs = find_diff_tags(first_tag_set, first_soup, legal_diffs)
	second_diffs = find_diff_tags(second_tag_set, second_soup, legal_diffs)
	return (set(first_diffs), set(second_diffs))
def find_diff_tags(tag_set, soup, legal_diffs):
	diff_tags = []
	cnt = 0
	tag_set_copy = tag_set.copy()
	for tag in tag_set:
		tags = soup.find_all(tag)
		for t in tags:
			for diff in legal_diffs:
				if diff in t.text:
					has_children = check_tag_for_nesting(t, tag_set_copy)
					if not has_children:
						diff_tags.append(t)
				for k,v in t.attrs.items():
					if diff in k or diff in v:
						has_children = check_tag_for_nesting(t, tag_set_copy)
						if not has_children:
							diff_tags.append(t)
	return diff_tags
def check_tag_for_nesting(tag, children):
	for child in children:
		value = check_for_children(tag, children)
		if value:
			return True
	return value
def check_for_children(tag, child):
	if tag.find(child):
		return True
	return False

def check_tags_for_token(tag_set, token):
	for t in tag_set:
		if token in t.text:
			return True
		for k,v in t.attrs.items():
			if token in k or token in v:
				return True
	return False
def write_alarm_file(flow, diff, token, cnt, legal_diffs, path):
	f_alarm = open(path + "alarm" + str(cnt), "w")
	f_alarm.write("Token: " + str(token) + " nije pronađen na adresi " + flow.request.path + "\n")
	f_alarm.write("Izlaz diffa: " + "\n" + str(diff) + "\n")
	f_alarm.write("Legitimne razlike koje su uzete u obzir: " + str(legal_diffs) + "\n")
	f_alarm.write("Proučite izlaz diffa, možda postoji još razlika koje treba navesti!")
	f_alarm.close()