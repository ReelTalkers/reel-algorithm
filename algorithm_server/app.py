from flask import Flask, request, jsonify
import recommendations
import io_utils


app = Flask(__name__)

datadir = "data/movielens/ml-latest-small"
ratings_matrix = io_utils.build_user_item_matrix(datadir)
movielens_to_imdb_bidict = io_utils.get_movie_links_dict(datadir, 'imdb')


@app.route('/recommendations', methods=['POST'])
def single_user_recommendations():
	new_user_ratings = io_utils.json_ratings_to_dict(request.get_json(), movielens_to_imdb_bidict)
	relevance_scores = recommendations.single_user_recommendation_vector(ratings_matrix, new_user_ratings)

	ranked_ids = recommendations.get_ranked_movielens_ids(ratings_matrix, relevance_scores, new_user_ratings.keys())
	movielens_top_k = recommendations.get_top_k_movielens_ids(ranked_ids, 100)

	return jsonify(["tt" + movielens_to_imdb_bidict[x] for x in movielens_top_k])


@app.route('/group_recommendations', methods=['POST'])
def group_recommendations():
    return jsonify(request.get_json())


if __name__ == '__main__':
    app.run(debug=True)
