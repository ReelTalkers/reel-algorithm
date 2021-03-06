from flask import Flask, request, jsonify
from algorithm_server.recommendations import *
import algorithm_server.io_utils as io_utils
from collections import *


app = Flask(__name__)


class App_Runner:

    @classmethod
    def set_globals(cls, datadir, log_filepath):
        global ratings_matrix
        global movielens_to_imdb_bidict
        global movielens_to_genre
        global movielens_to_year
        global legal_genres
        global recommenders
        global logfile

        ratings_matrix = io_utils.Matrix_Builder.build_matrix(datadir)
        movielens_to_imdb_bidict = io_utils.get_movie_links_dict(datadir)
        movielens_to_genre = io_utils.get_genre_mapping(datadir)
        movielens_to_year = io_utils.get_year_mapping(datadir)
        legal_genres = set().union(*[m for m in movielens_to_genre.values()])

        recommenders = {}
        recommenders["least_misery"] = Least_Misery_Recommender
        recommenders["disagreement_variance"] = Disagreement_Variance_Recommender

        logfile = log_filepath

    @classmethod
    def start_server(cls, datadir, log_filepath):
        App_Runner.set_globals(datadir, log_filepath)
        app.run(debug=False)


@app.route('/recommendations', methods=['POST'])
def recommendations():
    """
    Get recommendations for a group of users.

    See API doc for sample input and output.
    """

    json = request.get_json()

    method = parse_method(json)

    user_ratings = io_utils.get_user_rating_list(json, movielens_to_imdb_bidict)

    rated_movies = rated_movies_set(user_ratings)

    rvc = Recommendations_Vector_Collection.from_user_ratings(ratings_matrix, user_ratings)

    recommender = method(ratings_matrix)

    group_vector = recommender.group_recommendation_vector(rvc)

    scores = Movie_Scores.from_score_vector(ratings_matrix, group_vector, rated_movies)
    scores.filter_on_year(movielens_to_year, parse_min_year(json))

    quantity = parse_quantity(json)

    return jsonify(scores.output_as_genre_separated_keys_list(legal_genres, movielens_to_imdb_bidict, 
                                                                                  movielens_to_genre, quantity))


@app.route('/similar_movies', methods=['POST'])
def similar_movies():
    """
    Get movies that are similar to an input list of movies.

    See API doc for sample input and output.
    """

    json = request.get_json()

    min_year = parse_min_year(json)
    quantity = parse_quantity(json)
    movies = json.get('movies', [])

    movielens_movies = {movielens_to_imdb_bidict.inv[m] for m in movies}

    user_ratings = [{m: 5.0 for m in movielens_movies}]
    genres = set.union(*[movielens_to_genre[m] for m in movielens_movies])

    rvc = Recommendations_Vector_Collection.from_user_ratings(ratings_matrix, user_ratings)

    scores = Movie_Scores.from_score_vector(ratings_matrix, rvc.get_vector(0), set(movielens_movies))

    scores.filter_on_genres(movielens_to_genre, genres)
    scores.filter_on_year(movielens_to_year, min_year)
    scores.trim_to_top_k(quantity)
    scores.convert_indices_to_imdb(movielens_to_imdb_bidict)

    return jsonify(scores.output_as_keys_list())


def parse_quantity(json):
    return json.get("quantity", 100)


def parse_method(json):
    return recommenders.get(json.get("method", ""), Least_Misery_Recommender)


def parse_min_year(json):
    min_year = json.get("min_year", None)
    return (int(min_year) if min_year else min_year)


def rated_movies_set(user_ratings):
    return set().union(*[u.keys() for u in user_ratings])


def log(to_file):
    logger = open(logfile, "a")
    logger.write(to_file)
    logger.write("\n")
    logger.close()
