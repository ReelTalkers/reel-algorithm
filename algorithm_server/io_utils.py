from scipy.sparse import *


class User_Movie_Matrix:

    def __init__(self):
        #Map the user and movie ids from the MovieLens dataset to indices in the User-Movie matrix
        self.user_id_index = {}
        self.movie_id_index = {}

        self.temp_storage_dict = {}
        self.matrix = None

    def add_rating(self, user, movie, rating):
        self.update_index(self.user_id_index, user)
        self.update_index(self.movie_id_index, movie)
        self.temp_storage_dict[(user, movie)] = rating

    def update_index(self, index, identifier):
        if(identifier not in index):
            index[identifier] = len(index)

    def build_matrix(self):
        self.matrix = dok_matrix((len(self.user_id_index), len(self.movie_id_index)))
        for user, movie in self.temp_storage_dict:
            self.matrix[self.user_id_index[user], self.movie_id_index[movie]] = self.temp_storage_dict[(user, movie)]
        self.matrix = self.matrix.tocsr()


def ratings_file(datadir):
    return "%s/ratings.csv" % datadir


def movie_description_file(datadir):
    return "%s/movies.csv" % datadir

"""
Returns a generator in which each item is a tuple with the following fields ("userId", "movieId", "rating")
"""
def get_ratings_stream(datadir):
    reader = open(ratings_file(datadir), "r")
    for i, line in enumerate(reader.readlines()):
        if(i >= 1):
            yield tuple(str(line).strip().split(",")[:3])
    reader.close()


def build_user_item_matrix(datadir):
    matrix = User_Movie_Matrix()

    for userId, movieId, rating in get_ratings_stream(datadir):
        matrix.add_rating(int(userId), int(movieId), float(rating))

    matrix.build_matrix()
    return matrix

m = build_user_item_matrix("../data-small")
print(m.matrix)
