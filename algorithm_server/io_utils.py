from scipy.sparse import *
from bidict import bidict
import json


class User_Movie_Matrix:

    def __init__(self):
        #Map the user and movie ids from the MovieLens dataset to indices in the User-Movie matrix
        self.user_id_index = {}
        self.movie_id_index = bidict()

        self.temp_storage_dict = {}
        self.matrix = dok_matrix((1, 1))

    def get_shape(self):
        return self.matrix.shape

    def getrow(self, i):
        return self.matrix.getrow(i)

    def get_movielens_id(self, matrix_ind):
        return self.movie_id_index.inv[matrix_ind]

    def get_ratings_vector(self, preferences):
        """
        Converts a user's movie ratings using movie lens identifiers to an index
        based on the locations of movies in the User_Movie_Matrx

        @Param preferences: A mapping of (movieLens movie id) -> (user rating)

        Returns a dictionary with the same user ratings but instead mapping (matrix location) -> (user rating)
        Useful when we need to get user similarity profiles.
        """

        vector = csr_matrix((1, self.get_shape()[1]))
        for x in preferences:
            vector[0, self.movie_id_index[x]] = preferences[x]

        return vector

    def add_rating(self, user, movie, rating):
        self.update_index(self.user_id_index, user)
        self.update_index(self.movie_id_index, movie)
        self.temp_storage_dict[(user, movie)] = rating

    def update_index(self, index, identifier):
        if(identifier not in index):
            index[identifier] = len(index)

    def build_matrix(self):
        self.matrix = dok_matrix((len(self.user_id_index), len(self.movie_id_index)))
        for key, value in list(self.temp_storage_dict.items()):
            user, movie = key
            self.matrix[self.user_id_index[user], self.movie_id_index[movie]] = value
            del(self.temp_storage_dict[key])
        del(self.temp_storage_dict)
        self.matrix = self.matrix.tocsr()


def ratings_file(datadir):
    return "%s/ratings.csv" % datadir


def movie_description_file(datadir):
    return "%s/movies.csv" % datadir


def movie_links_file(datadir):
    return "%s/links.csv" % datadir


def get_ratings_stream(datadir):
    """
    Returns a generator in which each item is a tuple with the following fields ("userId", "movieId", "rating")
    """
    for i, line in enumerate(open(ratings_file(datadir), "r")):
        if(i >= 1):
            yield tuple(str(line).strip().split(",")[:3])


def get_movie_description_stream(datadir):
    for i, line in enumerate(open(movie_description_file(datadir), "r")):
        if(i >= 1):
            t = str(line).strip().split(",")
            if(len(t) > 3):
                middle = "".join(x for x in t[1:-1])
                t = (t[0], middle, t[-1])

            yield(tuple(t))


def get_links_stream(datadir):
    for i, line in enumerate(open(movie_links_file(datadir), "r")):
        if(i >= 1):
            yield tuple(str(line).strip().split(","))


def get_movie_links_dict(datadir, alt_id):
    """
    Returns a bidict that maps (movielens id) -> (alternate movie id (either 'imdb' or 'tmdb'))
    """
    links = bidict()

    identifiers = {'imdb': 1, 'tmdb': 2}

    if(alt_id not in identifiers):
        return links

    field = identifiers[alt_id]

    for line in get_links_stream(datadir):
        links[line[0]] = line[field]

    return links


def get_movie_id_title_dict(datadir):
    return {id: title for id, title, genre in get_movie_description_stream(datadir)}


def get_first_user_rating_dict(datadir):
    ratings = {}

    ratings_stream = get_ratings_stream(datadir)
    while(True):
        user, movie, rating = next(ratings_stream)
        if(not user == "1"):
            break
        ratings[movie] = float(rating)
    return ratings


def get_sample_ratings_dict(links_datadir, filepath, id_source='imdb'):
    """
    Returns a ratings dict that maps (movielens id) -> (rating) for ratings in a given filepath
    """
    ratings_dict = {}

    links = get_movie_links_dict(links_datadir, id_source)
    for line in open(filepath, 'r'):
        id, rating = tuple(line.split(" "))
        id = id[2:]
        rating = float(rating)

        if id in links.inv:
            ratings_dict[links.inv[id]] = rating

    return ratings_dict


def build_user_item_matrix(datadir):
    matrix = User_Movie_Matrix()

    for userId, movieId, rating in get_ratings_stream(datadir):
        matrix.add_rating(userId, movieId, float(rating))

    matrix.build_matrix()
    return matrix


def get_json_format_ratings_list(ratings_file):
    ratings = []
    for line in open(ratings_file, 'r'):
        rating_obj = {}
        rating_obj["imdb"], rating_obj["rating"] = line.strip().split(" ")
        ratings.append(rating_obj)
    return ratings


def get_json_query(ratings_file):
    query = {}
    query["ratings"] = get_json_format_ratings_list(ratings_file)
    return json.dumps(query)


def get_group_json_query(ratings_files):
    query = {}
    query["users"] = []
    for i, file in enumerate(ratings_files):
        user_obj = {}
        user_obj["user"], user_obj["ratings"] = file, get_json_format_ratings_list(file)
        query["users"].append(user_obj)
    return json.dumps(query)


if __name__ == "__main__":

    data_files = ["data/sample_users/%s" % s for s in ["andrew.txt", "galen.txt"]]

    print("Single user json:")
    print(get_json_query(data_files[0]))

    print("\n\nGroup json:")
    print(get_group_json_query(data_files))
