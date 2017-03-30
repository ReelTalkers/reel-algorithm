from flask import Flask, request, jsonify
from algorithm_server.recommendations import *
import algorithm_server.io_utils as io_utils
from collections import *


app = Flask(__name__)


@app.route('/recommendations', methods=['POST'])
def recommendations():
    json = request.get_json()

    quantity, agg_method, genre = parse_quantity(json), parse_method(json), parse_genre(json)

    user_ratings, cached_recs = io_utils.parse_mixed_user_ratings_cached_data(json, movielens_to_imdb_bidict)

    rated_movies = rated_movies_set(user_ratings)

    rvc = Recommendations_Vector_Collection.from_user_ratings(ratings_matrix, user_ratings)
    rvc += Recommendations_Vector_Collection.from_cached_scores(ratings_matrix, cached_recs)

    rec_vector = group_recommendation_vector(rvc, agg_method)

    movie_scores = Movie_Scores.from_score_vector(ratings_matrix, rec_vector, rated_movies, quantity)

    movie_scores.convert_indices_to_imdb(movielens_to_imdb_bidict)

    return (jsonify(movie_scores.output_as_keys_list()))


@app.route('/relevance_scores', methods=['POST'])
def relevance_scores():
    json = request.get_json()

    quantity, agg_method, genre = parse_quantity(json), parse_method(json), parse_genre(json)

    user_ratings = io_utils.get_user_rating_list(json, movielens_to_imdb_bidict)

    rated_movies = rated_movies_set(user_ratings)

    rvc = Recommendations_Vector_Collection.from_user_ratings(ratings_matrix, user_ratings)

    rec_vector = group_recommendation_vector(rvc, agg_method)

    movie_scores = Movie_Scores.from_score_vector(ratings_matrix, rec_vector, rated_movies, quantity)

    movie_scores.convert_indices_to_imdb(movielens_to_imdb_bidict)

    return jsonify(movie_scores.output_as_scores_list())


def parse_quantity(json):
    return json.get("quantity", 100)


def parse_method(json):
    return agg_methods.get(json.get("method", ""), least_misery_aggregation)


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

    ratings_matrix = io_utils.User_Movie_Matrix.from_datadir(datadir)
    movielens_to_imdb_bidict = io_utils.get_movie_links_dict(datadir)
    movielens_to_genre_bidict = io_utils.get_genre_mapping(datadir)

    agg_methods = {}
    agg_methods["least_misery"] = least_misery_aggregation
    agg_methods["disagreement_variance"] = disagreement_variance_aggregation


def start_server(datadir):
    set_globals(datadir)
    app.run(debug=True)
