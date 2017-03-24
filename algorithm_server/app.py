from flask import Flask, request, jsonify
import algorithm_server.recommendations as recommendations
import algorithm_server.io_utils as io_utils


app = Flask(__name__)


@app.route('/recommendations', methods=['POST'])
def single_user_recommendations():
    print(request.get_json())

    new_user_ratings = io_utils.json_ratings_to_dict(request.get_json()["ratings"], movielens_to_imdb_bidict)
    relevance_scores = recommendations.single_user_recommendation_vector(ratings_matrix, new_user_ratings)

    ranked_ids = recommendations.get_ranked_movielens_ids(ratings_matrix, relevance_scores, new_user_ratings.keys())
    movielens_top_k = recommendations.get_top_k_movielens_ids(ranked_ids, 100)

    return jsonify(["tt" + movielens_to_imdb_bidict[x] for x in movielens_top_k])


@app.route('/group_recommendations', methods=['POST'])
def group_recommendations():
    print(request.get_json())

    user_ratings = [io_utils.json_ratings_to_dict(u["ratings"], movielens_to_imdb_bidict) for u in request.get_json()["users"]]

    rated_movies = set().union(*[u.keys() for u in user_ratings])

    method = recommendations.group_recommendation_vector_least_misery

    ranked_ids = recommendations.get_ranked_movielens_ids(ratings_matrix, method(ratings_matrix, user_ratings), rated_movies)

    movielens_top_k = recommendations.get_top_k_movielens_ids(ranked_ids, 100)

    return jsonify(["tt" + movielens_to_imdb_bidict[x] for x in movielens_top_k])


def set_globals(datadir):
    global ratings_matrix
    global movielens_to_imdb_bidict

    ratings_matrix = io_utils.build_user_item_matrix(datadir)
    movielens_to_imdb_bidict = io_utils.get_movie_links_dict(datadir, 'imdb')


def start_server(datadir):
    set_globals(datadir)
    app.run(debug=True)
