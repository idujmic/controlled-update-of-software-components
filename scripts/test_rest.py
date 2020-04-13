import requests

def read_request_config(path):
	file = open(path, "r")
	request_dict = {}
	flag = False
	temp_dict = {}
	temp_key = ""
	for line in file:
		line = line.strip()
		if flag:
			if line != "}":
				if not line.strip():
					continue
				splitted_new = line.split(":")
				splitted_new = list(map(lambda s: s.strip(), splitted_new))
				temp_dict[splitted_new[0]] = splitted_new[1]
				request_dict[temp_key] = temp_dict
			else:
				flag = False 
				temp_dict = {}
				temp_key = ""
		else:
			splitted = line.split("=")
			splitted = list(map(lambda s: s.strip(), splitted))
			if len(splitted) > 2:
				query = ""
				for i in range(1, len(splitted) - 1):
					query += splitted[i] + "="
				query += splitted[len(splitted)-1]
				request_dict[splitted[0]] = query
			else:
				if splitted[1] != "{":
					request_dict[splitted[0]] = splitted[1]
				else :
					temp_key = splitted[0]
					request_dict[splitted[0]] = temp_dict
					flag = True
	return request_dict
def rest_api_request(url, headers = {}, data = "", method = 'GET'):
	print(url)
	r = requests.request(method, url, data = data, headers = headers)
	print(r)
request_dict = read_request_config("get_all.txt")
print(request_dict)
rest_api_request(request_dict["url"], request_dict["headers"], request_dict["payload"], request_dict["method"])
request_dict = read_request_config("get_blue.txt")
print(request_dict)
rest_api_request(request_dict["url"], request_dict["headers"], request_dict["payload"], request_dict["method"])
request_dict = read_request_config("delete_blue.txt")
print(request_dict)
rest_api_request(request_dict["url"], request_dict["headers"], request_dict["payload"], request_dict["method"])
request_dict = read_request_config("create_blue.txt")
print(request_dict)
rest_api_request(request_dict["url"], request_dict["headers"], request_dict["payload"], request_dict["method"])

