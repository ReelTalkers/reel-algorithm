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


print_response("Andrew recomendations:", "http://localhost:5000/recommendations", "data/sample_users/jsonified/andrew.json")
print("\n")
print_response("Group recommendations:", "http://localhost:5000/group_recommendations", "data/sample_users/jsonified/group.json")
