from scipy.sparse import *


class User_Movie_Matrix:

    def __init__(self):
        #Map the user and movie ids from the MovieLens dataset to indices in the User-Movie matrix
        self.user_id_index = {}
        self.movie_id_index = {}

        self.temp_storage_dict = {}
        self.matrix = dok_matrix((1, 1))

    def get_shape(self):
        return self.matrix.shape

    def getrow(self, i):
        return self.matrix.getrow(i)

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
            vector[0, x] = preferences[x]

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


def get_ratings_stream(datadir):
    """
    Returns a generator in which each item is a tuple with the following fields ("userId", "movieId", "rating")
    """
    for i, line in enumerate(open(ratings_file(datadir), "r")):
        if(i >= 1):
            yield tuple(str(line).strip().split(",")[:3])


def get_first_user_rating_dict(datadir):
    ratings = {}

    ratings_stream = get_ratings_stream(datadir)
    while(True):
        user, movie, rating = next(ratings_stream)
        if(not user == "1"):
            break
        ratings[int(movie)] = float(rating)
    return ratings


def build_user_item_matrix(datadir):
    matrix = User_Movie_Matrix()

    for userId, movieId, rating in get_ratings_stream(datadir):
        matrix.add_rating(int(userId), int(movieId), float(rating))

    print("Done adding ratings")

    matrix.build_matrix()
    return matrix


if __name__ == "__main__":

    m = build_user_item_matrix("../data/small")
    print(m.matrix)
