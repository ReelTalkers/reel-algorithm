from flask import Flask, request, jsonify
import algorithm_server.recommendations as recommendations
import algorithm_server.io_utils as io_utils
from collections import *


app = Flask(__name__)


"""
@app.route('/recommendations', methods=['POST'])
def recommendations():
"""


@app.route('/relevance_scores', methods=['POST'])
def relevance_scores():
    json = request.get_json()

    user_ratings = [io_utils.json_ratings_to_dict(u["ratings"], movielens_to_imdb_bidict) for u in json["users"]]

    quantity = json.get("quantity", 100)

    rated_movies = set().union(*[u.keys() for u in user_ratings])

    method = recommendation_methods.get(json.get("method", ""), recommendations.group_recommendation_vector_least_misery)

    ranked_ids = recommendations.get_ranked_movielens_ids(ratings_matrix, method(ratings_matrix, user_ratings), rated_movies, quantity)

    return jsonify({"tt" + movielens_to_imdb_bidict[key]: value for key, value in ranked_ids.items()})


def set_globals(datadir):
    global ratings_matrix
    global movielens_to_imdb_bidict
    global recommendation_methods

    ratings_matrix = io_utils.build_user_item_matrix(datadir)
    movielens_to_imdb_bidict = io_utils.get_movie_links_dict(datadir, 'imdb')

    recommendation_methods = {}
    recommendation_methods["least_misery"] = recommendations.group_recommendation_vector_least_misery
    recommendation_methods["disagreement_variance"] = recommendations.group_recommendation_vector_disagreement_variance


def start_server(datadir):
    set_globals(datadir)
    app.run(debug=True)
