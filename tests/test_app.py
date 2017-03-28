from algorithm_server import io_utils as io_utils
from algorithm_server import recommendations
from algorithm_server import app as app
import json


ratings_files = ["data/sample_users/andrew.txt", "data/sample_users/galen.txt"]
datadir = "data/movielens/ml-latest-small"

client = app.app.test_client()
app.set_globals(datadir)


def test_relevance_scores_endpoint():
    d = io_utils.read_json_from_file("data/sample_users/jsonified/group.json")

    response = client.post('/relevance_scores', data=json.dumps(d), content_type='application/json')

    print(response.data)
