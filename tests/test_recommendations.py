from algorithm_server import io_utils as io_utils
from algorithm_server import recommendations as r
import collections

ratings_files = ["data/sample_users/andrew.txt", "data/sample_users/galen.txt"]
datadir = "data/movielens/ml-latest-small"


def test_group_recommendations_disagr_var():
    num_movies = 100

    movie_titles = io_utils.get_movie_id_title_dict(datadir)

    group_ids = r.get_group_movielens_ids_from_file(ratings_files, datadir, method=r.group_recommendation_vector_disagreement_variance)

    assert type(group_ids) == collections.OrderedDict

    top_ids = r.get_top_k_movielens_ids(group_ids, num_movies)

    assert len(top_ids) == num_movies

    print(top_ids)
