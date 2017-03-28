from flask import Flask, request, jsonify
import algorithm_server.recommendations as recommendations
import algorithm_server.io_utils as io_utils
from collections import *


app = Flask(__name__)


@app.route('/recommendations', methods=['POST'])
def recommendations():
    json = request.get_json()

    quantity, agg_method, genre = parse_quantity(json), parse_method(json), parse_genre(json)

    user_ratings, cached_recommendations = io_utils.parse_mixed_user_ratings_cached_data(users["json"], movielens_to_imdb_bidict)

    cached_vectors = convert_movie_score_dicts_to_vectors(cached_recommendations)

    rec_vector = group_recommendation_vector_from_cache(ratings_matrix, user_ratings, cached_vectors, agg_method)

    movie_scores = recommendations.get_movie_scores(ratings_matrix, rec_vector, rated_movies, quantity)

    return (jsonify(["tt" + movielens_to_imdb_bidict[key] for key in movie_scores.keys()]))


@app.route('/relevance_scores', methods=['POST'])
def relevance_scores():
    json = request.get_json()

    quantity, agg_method, genre = parse_quantity(json), parse_method(json), parse_genre(json)

    user_ratings = io_utils.get_user_rating_list(json["users"], movielens_to_imdb_bidict)

    rated_movies = rated_movies_set(user_ratings)

    rec_vector = group_recommendation_vector(ratings_matrix, user_ratings, agg_method)

    movie_scores = recommendations.get_movie_scores(ratings_matrix, rec_vector, rated_movies, quantity)

    return jsonify({"tt" + movielens_to_imdb_bidict[key]: value for key, value in movie_scores.items()})


def parse_quantity(json):
    return json.get("quantity", 100)


def parse_method(json):
    return recommendation_methods.get(json.get("method", ""), recommendations.least_misery_aggregation)


def parse_genre(json):
    genre = json.get("genre", None)
    if(genre and genre not in movielens_to_genre_bidict.values()):
        genre = None
    return genre


def rated_movies_set(user_ratings):
    return set().union(*[u.keys() for u in user_ratings])


def set_globals(datadir):
    global ratings_matrix
    global movielens_to_imdb_bidict
    global movielens_to_genre_bidict
    global agg_methods

    ratings_matrix = io_utils.build_user_item_matrix(datadir)
    movielens_to_imdb_bidict = io_utils.get_movie_links_dict(datadir, 'imdb')
    movielens_to_genre_bidict = io_utils.get_genre_mapping(datadir)

    agg_methods = {}
    agg_methods["least_misery"] = recommendations.least_misery_aggregation
    agg_methods["disagreement_variance"] = recommendations.disagreement_variance_aggregation


def start_server(datadir):
    set_globals(datadir)
    app.run(debug=True)
