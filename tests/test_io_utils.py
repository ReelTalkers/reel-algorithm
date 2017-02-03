from algorithm_server import io_utils


def test_ratings_stream():
    user_movie_combinations = set()

    stream = io_utils.get_ratings_stream("data-small")
    for i in stream:
        t = (i[0], i[1])
        assert(t not in user_movie_combinations)
        user_movie_combinations.add(t)


def test_movie_id_location_map():
    m = io_utils.map_movie_id_to_matrix_location("data-small")
    for key in m.keys():
        assert(m[key] in range(0, len(m) + 1))


def test_build_user_movie_matrix_as_dict():
    dimension, umm = io_utils.build_user_movie_matrix_as_dict("data-small")
    print(dimension)
