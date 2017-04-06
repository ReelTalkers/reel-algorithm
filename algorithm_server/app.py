from flask import Flask, request, jsonify
from algorithm_server.recommendations import *
import algorithm_server.io_utils as io_utils
from collections import *


app = Flask(__name__)


@app.route('/recommendations', methods=['POST'])
def recommendations():
    return jsonify(movie_scores_from_json(request.get_json()).output_as_keys_list())


@app.route('/relevance_scores', methods=['POST'])
def relevance_scores():
    return jsonify(movie_scores_from_json(request.get_json()).output_as_scores_list())


def movie_scores_from_json(json):
    quantity, method, genre = parse_quantity(json), parse_method(json), parse_genre(json)

    user_ratings, cached_recs = io_utils.parse_mixed_user_ratings_cached_data(json, movielens_to_imdb_bidict)

    rated_movies = rated_movies_set(user_ratings)

    rvc = Recommendations_Vector_Collection.from_user_ratings(ratings_matrix, user_ratings)
    if(len(cached_recs) > 0):
        rvc += Recommendations_Vector_Collection.from_cached_scores(ratings_matrix, cached_recs)

    recommender = method(ratings_matrix)

    group_vector = recommender.group_recommendation_vector(rvc)

    movie_scores = Movie_Scores.from_score_vector(ratings_matrix, group_vector, rated_movies)

    movie_scores.filter_on_genre(genre, movielens_to_genre_bidict)

    movie_scores.trim_to_top_k(quantity)

    movie_scores.convert_indices_to_imdb(movielens_to_imdb_bidict)

    return movie_scores


def parse_quantity(json):
    return json.get("quantity", 100)


def parse_method(json):
    return recommenders.get(json.get("method", ""), Least_Misery_Recommender)


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
    global recommenders

    ratings_matrix = io_utils.User_Movie_Matrix.from_datadir(datadir)
    movielens_to_imdb_bidict = io_utils.get_movie_links_dict(datadir)
    movielens_to_genre_bidict = io_utils.get_genre_mapping(datadir)

    recommenders = {}
    recommenders["least_misery"] = Least_Misery_Recommender
    recommenders["disagreement_variance"] = Disagreement_Variance_Recommender


def start_server(datadir):
    set_globals(datadir)
    app.run(debug=True)
