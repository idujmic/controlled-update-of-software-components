from bs4 import BeautifulSoup
from mitmproxy import io, http
from mitmproxy import ctx
from mitmproxy import connections
from diff_match_patch import diff_match_patch
import difflib
from pprint import pprint
import sys
class FlowComparator:
	def __init__(self):
		self.cnt = 0

	def compare_content(self, first_content, second_content):
		first_soup = BeautifulSoup(first_content.response.content, "html.parser")
		second_soup = BeautifulSoup(second_content.response.content, "html.parser")
		file_one = open("html_one" + str(self.cnt) + ".html", "w")
		file_two = open("html_two" + str(self.cnt) + ".html", "w")
		file_one.write(str(first_content.request.path) + '\n')
		file_two.write(str(second_content.request.path) + '\n')
		for line_one, line_two in zip(first_soup, second_soup):
			file_one.write(str(line_one))
			file_two.write(str(line_two))
		self.cnt +=1
		file_one.close()
		file_two.close()

	def diff_content(self, first_content, second_content):
		first_soup = BeautifulSoup(first_content.response.content, "html.parser")
		second_soup = BeautifulSoup(second_content.response.content, "html.parser")
		dmp = diff_match_patch()
		patches = dmp.patch_make(str(first_soup.prettify()), str(second_soup.prettify()))
		diff = dmp.patch_toText(patches)
		file = open("diff_" + str(self.cnt) + ".html", "w")
		file.write(str(diff))
		file.close()		
		file_one = open("first_html_" + str(self.cnt), "w")
		file_two = open("second_html_" + str(self.cnt), "w")
		self.cnt +=1
		file_one.write(str(first_soup.prettify()))
		file_two.write(str(second_soup.prettify()))
		file_one.close()
		file_two.close()
	
	def diff_line(self, first_content, second_content):
		first_soup = BeautifulSoup(first_content.response.content, "html.parser")
		second_soup = BeautifulSoup(second_content.response.content, "html.parser")
		file = open("razlike_" + str(self.cnt), "w")
		line_counter = 0
		for line_one, line_two in zip(first_soup, second_soup):
			dmp = diff_match_patch()
			patches = dmp.patch_make(str(line_one), str(line_two))
			diff = dmp.patch_toText(patches)
			if len(str(diff)) != 0:
				file.write("Razlika u retku " + str(line_counter))
				file.write("Prvi odgovor: " + str(line_one))
				file.write("Drugi odogovor: " + str(line_two))
			line_counter+=1
		file.close()
		self.cnt += 1

	def difference(self, first_content, second_content):
		first_soup = BeautifulSoup(first_content.response.content, "html.parser")
		second_soup = BeautifulSoup(second_content.response.content, "html.parser")
		first_tree = first_soup.find_all()
		second_tree = second_soup.find_all()
		line_counter = 0
		has_difference = False
		for first_tag, second_tag in zip(first_tree, second_tree):
			dmp = diff_match_patch()
			patches = dmp.patch_make(str(first_tag), str(second_tag))
			diff = dmp.patch_toText(patches)
			if len(str(diff)) != 0:
				if not has_difference:
					file = open("diff" + str(self.cnt), "w")
					has_difference = True
				file.write("Razlika u retku " + str(line_counter))
				file.write("Prvi odgovor: " + str(first_tag))
				file.write("Drugi odogovor: " + str(second_tag))	
			line_counter+=1	
		self.cnt +=1
		file.close()

	def test(self, first_content, second_content):
		first_content = first_content.response.content
		second_content = second_content.response.content
		first_soup = BeautifulSoup(first_content, "html.parser")
		file = open("test" + str(self.cnt), "w")
		for a in first_soup:
			for line in a:
				file.write("Redak " + str(line) + "\n")
		file.close()
		self.cnt+=1


	def differ(self, first_content, second_content):
		sys.stdout = open("differ" + str(self.cnt), "w")
		first_soup  = BeautifulSoup(first_content.response.content, "html.parser")
		second_soup = BeautifulSoup(second_content.response.content, "html.parser")
		d = difflib.Differ()
		for x,y in zip(first_soup, second_soup):
			x = str(x).splitlines(keepends=True)
			y = str(y).splitlines(keepends=True)
			result = list(d.compare(x, y))
			pprint(result)
		self.cnt+=1


	def string_compare(self, first_content, second_content):
		first_content = str(first_content.response.content)
		second_content = str(second_content.response.content)
		line_counter = 0

		has_difference = False

		for a,b in zip(first_content, second_content):
			if a != b:
				if not has_difference:
					file = open("diff" + str(self.cnt), "w")
					has_difference = True
				file.write("Razlika u retku " + str(line_counter) + "\n")
				file.write("+ " + a + "\n")
				file.write("- " + b + "\n")
			line_counter+=1
		self.cnt +=1




