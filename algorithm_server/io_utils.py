from bidict import bidict


def ratings_file(datadir):
    return "%s/ratings.csv" % datadir


def movie_description_file(datadir):
    return "%s/movies.csv" % datadir


def get_ratings_stream(datadir):
    reader = open(ratings_file(datadir), "r")
    for i, line in enumerate(reader.readlines()):
        if(i >= 1):
            yield tuple(str(line).strip().split(",")[:3])
    reader.close()


def map_movie_id_to_matrix_location(datadir):
    matrix_loc_map = bidict()

    reader = open(movie_description_file(datadir), "r")
    for i, line in enumerate(reader.readlines()):
        if(i >= 1):
            comma_pos = line.find(",")
            if(comma_pos > 0):
                matrix_loc_map[line[:comma_pos]] = i

    return matrix_loc_map


def build_user_movie_matrix_as_dict(datadir):
    user_movie_dict = dict()
    unique_users = set()

    movie_id_locs = map_movie_id_to_matrix_location(datadir)
    ratings_stream = get_ratings_stream(datadir)

    for user_id, movie_id, rating in ratings_stream:
        user_movie_dict[(int(user_id) + len(movie_id_locs), movie_id_locs[movie_id])] = rating
        unique_users.add(user_id)

    return len(unique_users) + len(movie_id_locs), user_movie_dict
