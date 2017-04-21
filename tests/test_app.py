from algorithm_server import io_utils as io_utils
from algorithm_server import recommendations
from algorithm_server import app as app
import json


ratings_files = ["data/sample_users/andrew.txt", "data/sample_users/galen.txt"]
datadir = "data/movielens/ml-latest-small"

client = app.app.test_client()
app.set_globals(datadir, "log.txt")

print("Finished loading matrix")


def test_similar_to_childrens_movies():
	popular_childrens_movies = io_utils.get_most_popular_movies_of_genre(datadir, "Horror", 10)

	movielens_to_imdb = io_utils.get_movie_links_dict(datadir)
	title_map = io_utils.get_title_mapping(datadir)

	movies = [movielens_to_imdb[x] for x in popular_childrens_movies]
	print(movies)

	request = {}
	request["quantity"] = 100
	request["movies"] = movies
	request["min_year"] = 2006

	response = client.post('/similar_movies', data=json.dumps(request), content_type='application/json')

	imdb_response = json.loads(response.data.decode('utf-8'))

	movielens_response = [movielens_to_imdb.inv[x] for x in imdb_response]

	print([title_map[x] for x in movielens_response])

	assert len(imdb_response) == 100
