from bs4 import BeautifulSoup
from diff_match_patch import diff_match_patch
import sys
import json
class FlowComparator:
	def __init__(self, legal_diffs):
		self.cnt = 0
		self.legal_diffs = legal_diffs
	def diff_content(self, first_flow, second_flow):
		if "Content-Type" in first_flow.response.headers:				
			if "json" in first_flow.response.headers["Content-Type"]:
				self.diff_json(first_flow, second_flow)
			else: 
				self.diff_html(first_flow, second_flow)
	def diff_html(self, first_flow, second_flow):
		first_soup = BeautifulSoup(first_flow.response.content, "html.parser")
		second_soup = BeautifulSoup(second_flow.response.content, "html.parser")
		dmp = diff_match_patch()
		patches = dmp.patch_make(str(first_soup.prettify()), str(second_soup.prettify()))
		diff = dmp.patch_toText(patches)
		if len(str(diff)) != 0:
			file = open("test_new_compare/diff_" + str(self.cnt), "w")
			file.write(first_flow.request.path + "\n")
			file.write(diff)
			file.close()
			first_diff_tags, second_diff_tags = get_legal_diffs_from_response(first_soup, second_soup, self.legal_diffs)
			file = open("test_new_compare/diff_" + str(self.cnt), "r")
			for line in file:
				token = line[1:len(line)-1]
				if line[0] == "-":
					if not check_tags_for_token(first_diff_tags, token):
						write_alarm_file(first_flow, diff, token, self.cnt, self.legal_diffs)
				elif line[0] == "+":
					if not check_tags_for_token(second_diff_tags, token):
						write_alarm_file(second_flow, diff, token, self.cnt, self.legal_diffs)
				else:
					continue
			file.close()
		file_one = open("test_new_compare/first_html_" + str(self.cnt) + ".html", "w")
		file_two = open("test_new_compare/second_html_" + str(self.cnt) + ".html", "w")
		file_one.write(str(first_soup.prettify()))
		file_two.write(str(second_soup.prettify()))
		file_one.close()
		file_two.close()
		self.cnt+=1
	def diff_json(self, first_content, second_content):
		first_soup = BeautifulSoup(first_content.response.content, "html.parser")
		second_soup = BeautifulSoup(second_content.response.content, "html.parser")
		dmp = diff_match_patch()
		patches = dmp.patch_make(str(first_soup.prettify()), str(second_soup.prettify()))
		diff = dmp.patch_toText(patches)
		if len(diff) > 0:
			file = open("test_new_compare/colour_diff" + str(self.cnt), "w")
			file.write(first_content.request.path + "\n")
			file.write(diff)
			file.close()
			first_json_dict=json.loads(str(first_soup))
			second_json_dict = json.loads(str(second_soup))
			file = open("test_new_compare/colour_diff" + str(self.cnt), "r")
			for line in file:
				token = line[1:len(line)-1]
				if line[0] == "-":
					check_json_alarm(first_json_dict, token, self.legal_diffs, diff, self.cnt, first_content)
				elif line[1] == "+":
					check_json_alarm(second_json_dict, token, self.legal_diffs, diff, self.cnt, second_content)
				else:
					continue
			file.close()
		file_one = open("test_new_compare/first_html_" + str(self.cnt) + ".html", "w")
		file_two = open("test_new_compare/second_html_" + str(self.cnt) + ".html", "w")
		file_one.write(str(first_soup.prettify()))
		file_two.write(str(second_soup.prettify()))
		file_one.close()
		file_two.close()
		self.cnt +=1
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
	for tag in tag_set:
		tags = soup.find_all(tag)
		for t in tags:
			for k,v in t.attrs.items():
				for diff in legal_diffs:
					if diff in k or diff in v:
						diff_tags.append(t)
	return diff_tags
def check_tags_for_token(tag_set, token):
	flag = False
	for t in tag_set:
		for k,v in t.attrs.items():
			if token in k or token in v:
				return True
	return False
def write_alarm_file(flow, diff, token, cnt, legal_diffs):
	f_alarm = open("test_new_compare/alarm" + str(cnt), "w")
	f_alarm.write("Token: " + token + " nije pronađen na adresi " + flow.request.path + "\n")
	f_alarm.write("Izlaz diffa: " + "\n" + str(diff) + "\n")
	f_alarm.write("Legitimne razlike koje su uzete u obzir: " + str(legal_diffs) + "\n")
	f_alarm.write("Proučite izlaz diffa, možda postoji još razlika koje treba navesti!")
	f_alarm.close()