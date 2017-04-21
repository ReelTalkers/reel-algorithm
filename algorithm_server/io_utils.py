from scipy.sparse import *
from bidict import bidict


class User_Movie_Matrix:

    ratings_adjustment = -3

    @classmethod
    def from_datadir(cls, datadir):
        matrix = cls(get_matrix_dimension(datadir))

        for userId, movieId, rating in get_ratings_stream(datadir):
            matrix.add_rating(userId, movieId, float(rating))

        #matrix.update_columns_sum_vector()
        matrix.convert_to_csr()
        return matrix

    def __init__(self, dimension):
        #Map the user and movie ids from the MovieLens dataset to indices in the User-Movie matrix
        self.user_id_index = {}
        self.movie_id_index = bidict()

        self.matrix = dok_matrix(dimension)
        self.column_sums = dok_matrix((1, dimension[1]))
        self.num_ratings = 0

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
            vector[0, self.movie_id_index[x]] = preferences[x] + self.ratings_adjustment

        return vector


    def add_rating(self, user, movie, rating):
        self.update_index(self.user_id_index, user)
        self.update_index(self.movie_id_index, movie)
        self.column_sums[0, self.movie_id_index[movie]] += 1
        self.num_ratings += 1
        self.matrix[self.user_id_index[user], self.movie_id_index[movie]] = rating + self.ratings_adjustment

    def update_index(self, index, identifier):
        if(identifier not in index):
            index[identifier] = len(index)

    def update_columns_sum_vector(self):
        for i in range(self.matrix.shape[1]):
            col = self.matrix.getcol(i)
            self.column_sums[0, i] = self.matrix.getcol(i).getnnz()

        self.column_sums = self.column_sums.tocsr()

    def convert_to_csr(self):
        self.column_sums = self.column_sums.tocsr()
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


def get_matrix_dimension(datadir):
    users = set()
    movies = set()

    for user, movie, rating in get_ratings_stream(datadir):
        users.add(user)
        movies.add(movie)

    return len(users), len(movies)


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
        movielens = line[0]
        imdb = "tt" + line[1]

        if(not (movielens in links or imdb in links.inv)):
            links[line[0]] = "tt" + line[1]

    return links


def get_title_mapping(datadir):
    title_map = {}

    for id, title, genre in get_movie_description_stream(datadir):
        title_map[id] = str(title)

    return title_map
    

def get_genre_mapping(datadir):
    genre_map = {}
    for id, title, genre in get_movie_description_stream(datadir):
        genre_map[id] = set(genre.split("|"))

    return genre_map


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


def parse_mixed_user_ratings_cached_data(json_ratings, movielens_to_imdb_bidict):
    user_ratings = []
    cached_data = []

    for user in json_ratings["users"]:
        if("is_cached" not in user or not user["is_cached"]):
            user_ratings.append(json_ratings_to_dict(user["ratings"], movielens_to_imdb_bidict))
        else:
            cached_data.append(json_ratings_to_dict(user["ratings"], movielens_to_imdb_bidict, field_name="score"))

    return user_ratings, cached_data

def get_most_popular_movies_of_genre(datadir, genre, quantity):
    genre_map = get_genre_mapping(datadir)

    movies_of_genre = {x for x in genre_map.keys() if genre in genre_map[x]}

    total_stars = {}

    for uid, movie, rating in get_ratings_stream(datadir):
        if(movie in movies_of_genre):
            total_stars[movie] = total_stars.get(movie, 0.0) + float(rating)

    return list(sorted(total_stars.keys(), key=lambda x: total_stars[x], reverse=True))[:quantity]

def get_year_mapping(datadir):
    movielens_to_year = {}

    for movielens, title, genres in get_movie_description_stream(datadir):
        try:
            movielens_to_year[movielens] = int(title[title.rfind("(") + 1: title.rfind(")")])
        except:
            movielens_to_year[movielens] = 1900

    return movielens_to_year


