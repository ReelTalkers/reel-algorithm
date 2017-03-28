import requests
import json


def get_json(filename):
	f = open(filename, "r")
	data = dict(json.loads(f.read()))
	f.close()
	return data


def print_response(tag, endpoint, json_file):
	print(tag)
	print(requests.post(endpoint, json=get_json(json_file)).json())


print_response("Group recommendations:", "http://localhost:5000/relevance_scores", "data/sample_users/jsonified/group.json")
