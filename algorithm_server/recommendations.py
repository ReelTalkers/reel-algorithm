import io_utils
import scipy.sparse as sp
import sklearn.preprocessing as sk


class Ratings_Matrix:

    def __init__(self):
        self.initialized = False
        self.positive_rating_matrix = None
        self.negative_rating_matrix = None

    def load_from_file(self, datadir):
        dimension, user_movies_ratings_dict = io_utils.build_user_movie_matrix_as_dict(datadir)

        self.positive_rating_matrix = sp.dok_matrix((dimension, dimension))
        self.negative_rating_matrix = sp.dok_matrix((dimension, dimension))
        for key in user_movies_ratings_dict.keys():
            user, movie = key
            rating = float(user_movies_ratings_dict[key])

            if(rating < 3.0):
                self.negative_rating_matrix[user, movie] = 1.0
                self.negative_rating_matrix[movie, user] = 1.0
            else:
                self.positive_rating_matrix[user, movie] = 1.0
                self.positive_rating_matrix[movie, user] = 1.0

        self.positive_rating_matrix = sk.normalize(self.positive_rating_matrix.tocsr(), norm="l1")
        self.negative_rating_matrix = sk.normalize(self.negative_rating_matrix.tocsr, norm="l1")



    #user_preferences should be a dictionary mapping {movie_id -> rating}
    def make_recommendations(self, user_preferences):
        return None
