from algorithm_server import io_utils


def test_ratings_stream():
    user_movie_combinations = set()

    stream = io_utils.get_ratings_stream("data-small/ratings.csv")
    for i in stream:
        t = (i[0], i[1])
        assert(t not in user_movie_combinations)
        user_movie_combinations.add(t)


def test_movie_id_location_map():
    m = io_utils.map_movie_id_to_matrix_location("data-small/movies.csv")
    for key in m.keys():
        assert(m[key] in range(0, len(m) + 1))
