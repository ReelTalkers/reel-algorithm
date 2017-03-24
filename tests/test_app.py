from algorithm_server import io_utils as io_utils
from algorithm_server import recommendations
from algorithm_server import app as app
import json


ratings_files = ["data/sample_users/andrew.txt", "data/sample_users/galen.txt"]
datadir = "data/movielens/ml-latest-small"

client = app.app.test_client()
app.set_globals(datadir)


def test_group_recommendations_removes_previously_seen():
    request = io_utils.read_json_from_file("data/sample_users/jsonified/dissimilar_group.json")

    movielens_to_imdb_bidict = io_utils.get_movie_links_dict(datadir, 'imdb')

    user_ratings = [io_utils.json_ratings_to_dict(u["ratings"], movielens_to_imdb_bidict) for u in request["users"]]

    rated_movies = set().union(*[u.keys() for u in user_ratings])

    method = recommendations.group_recommendation_vector_least_misery

    ratings_matrix = io_utils.build_user_item_matrix(datadir)

    ranked_ids = recommendations.get_ranked_movielens_ids(ratings_matrix, method(ratings_matrix, user_ratings), rated_movies)

    movielens_top_k = recommendations.get_top_k_movielens_ids(ranked_ids, 100)

    assert(len(rated_movies.intersection(set(movielens_top_k))) == 0)


def test_group_recommendations_endpoint():
    d = io_utils.read_json_from_file("data/sample_users/jsonified/group.json")

    movies = sum([u["ratings"] for u in d["users"]], [])
    movies = [m["imdb"] for m in movies]

    response = client.post('/group_recommendations', data=json.dumps(d), content_type='application/json')

    ids = [x[x.find("\"") + 1: x.rfind("\"")] for x in str(response.data).split(sep=",")]

    assert(len(set(ids).intersection(set(movies))) == 0)
