from scipy.sparse import *
from bidict import bidict


class User_Movie_Matrix:

    @classmethod
    def from_datadir(cls, datadir):
        matrix = cls()

        for userId, movieId, rating in get_ratings_stream(datadir):
            matrix.add_rating(userId, movieId, float(rating))

        matrix.build_matrix()
        return matrix

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
        self.temp_storage_dict[(user, movie)] = rating - 3

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


def get_movie_links_dict(datadir):
    """
    Returns a bidict that maps (movielens id) -> (imdb id)
    """
    links = bidict()

    for line in get_links_stream(datadir):
        links[line[0]] = "tt" + line[1]

    return links


def json_ratings_to_dict(json_ratings, movielens_to_imdb, field_name="rating"):
    ratings = {}
    for item in json_ratings:
        imdb_id = item["imdb"]
        rating = float(item[field_name])
        if(imdb_id in movielens_to_imdb.inv):
            ratings[movielens_to_imdb.inv[imdb_id]] = rating

    return ratings


def get_user_rating_list(json_ratings, movielens_to_imdb_bidict):
    return [json_ratings_to_dict(u["ratings"], movielens_to_imdb_bidict) for u in json_ratings["users"]]


def get_genre_mapping(datadir):
    return {}


def parse_mixed_user_ratings_cached_data(json_ratings, movielens_to_imdb_bidict):
    user_ratings = []
    cached_data = []

    for user in json_ratings["users"]:
        if("is_cached" not in user or not user["is_cached"]):
            user_ratings.append(json_ratings_to_dict(user["ratings"], movielens_to_imdb_bidict))
        else:
            cached_data.append(json_ratings_to_dict(user["ratings"], movielens_to_imdb_bidict, field_name="score"))

    return user_ratings, cached_data
