import scipy.sparse as sp
from collections import OrderedDict
from bidict import bidict
import math


class User_Movie_Matrix:
    """
    Data structure that contains the User-Movie ratings matrix from the MovieLens dataset.
    To get an instance of this datastructure, call io_utils.build_matrix()
    """

    #Ratings are adjusted to be in the range (-2.5, 2.0)
    ratings_adjustment = -3

    def __init__(self, dimension):
        #Map the user and movie ids from the MovieLens dataset to indices in the User-Movie matrix
        self.user_id_index = {}
        self.movie_id_index = bidict()

        #matrix and vector of column sums of the matrix
        self.matrix = sp.dok_matrix(dimension)
        self.scaled_column_sums = sp.dok_matrix((1, dimension[1]))

        #vector of the top movies for a generic user
        self.top_movies = None

    def initialize_top_movies(self):
        user_dim = self.matrix.get_shape()[0]

        user_similarities = sp.dok_matrix((1, user_dim))
        for i in range(user_dim):
            user_similarities[0, i] = 1 / user_dim

        user_similarities = user_similarities.tocsr()

        self.top_movies = user_similarities.dot(self.matrix)

    def initialize_scaled_column_sums(self):
        for i in range(self.scaled_column_sums.get_shape()[1]):
            self.scaled_column_sums[0, i] = (1 + math.log(self.scaled_column_sums[0, 1], 2))
        self.scaled_column_sums = self.scaled_column_sums.tocsr()

    def get_top_movies(self):
        return self.top_movies

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

        vector = sp.dok_matrix((1, self.get_shape()[1]))
        for x in preferences:
            vector[0, self.movie_id_index[x]] = preferences[x] + self.ratings_adjustment

        return vector.tocsr()

    def normalize_score_vector(self, scores):
        for i in range(scores.get_shape()[1]):
            scores[0, i] /= self.scaled_column_sums[0, i]
        return scores

    def add_rating(self, user, movie, rating):
        self.update_index(self.user_id_index, user)
        self.update_index(self.movie_id_index, movie)
        self.scaled_column_sums[0, self.movie_id_index[movie]] += 1
        self.matrix[self.user_id_index[user], self.movie_id_index[movie]] = rating + self.ratings_adjustment

    def update_index(self, index, identifier):
        if(identifier not in index):
            index[identifier] = len(index)


class Aggregation_Functions:
    """
    Contains aggregation functions for generating group recommendations.

    The aggregation functions operate on a list of scores (floats) and return a single float.

    Used by the Group_Recommender class and all subclasses.
    """

    @classmethod
    def highest_score_agg(cls, values, **kwargs):
        return max(values)

    @classmethod
    def least_misery_agg(cls, values, **kwargs):
        return min(values)

    @classmethod
    def disagreement_variance_agg(cls, values, **kwargs):
        mean_weight = kwargs.get('mean_weight', .8)
        mean = sum(values) / len(values)
        var = sum((i - mean) ** 2 for i in values) / len(values)
        return mean_weight * mean + (1 - mean_weight) * (1 - var)


class Recommender:
    """
    Provides a recommendation vector for a single user.
    """

    def __init__(self, ratings_matrix):
        """
        ratings_matrix is a |U|x|M| matrix composed of prior user ratings
        """
        self.ratings_matrix = ratings_matrix

    def single_user_recommendation_vector(self, user_ratings):
        """
        Computes a 1x|M| movie recommendation vector for a given user.
        rating_vector is a 1x|M| sparse vector of user ratings
        """

        ratings_vector = self.ratings_matrix.get_ratings_vector(user_ratings)

        user_similarity_profile = self.calculate_user_similarity_profile(ratings_vector)

        return self.calculate_item_relevance_scores(user_similarity_profile)

    def calculate_user_similarity_profile(self, ratings_vector):
        """
        rating_vector is a 1x|M| sparse vector of userr ratings

        We want to return a 1x|U| dense user similiarity vector

        """
        num_users, num_movies = self.ratings_matrix.get_shape()

        user_similarities = sp.dok_matrix((1, num_users))
        for i in range(num_users):

            user_similarities[0, i] = self.calculate_pairwise_user_similarity(self.ratings_matrix.getrow(i), ratings_vector)

        return user_similarities.tocsr()

    def calculate_pairwise_user_similarity(self, user1_preferences, user2_preferences):
        """
        Both user preferences parameters are sparse 1x|M| vectors corresponding to movie ratings.
        Computes a scalar value (float in range (0, 1)), that corresponds to how similar the users are.

        User similarity = (number of movie agreements) / (number of shared reviews)
        A movie agreement is defined as a movie for which the ratings of the two users were within 2 stars of each other
        A shared review is defined as a movie for which both users provided a review

        """

        shared_items = set(user1_preferences.indices) & set(user2_preferences.indices)

        all_items = set(user1_preferences.indices) | set(user2_preferences.indices)

        num_agreements = sum(1 for x in shared_items if abs(user1_preferences[0, x] - user2_preferences[0, x]) <= 2)

        return (num_agreements / len(all_items) if len(all_items) > 0 else 0)

    def calculate_item_relevance_scores(self, user_similarity_profile):
        """
        Calculates item relevance scores for each item in the |U|x|M| ratings matrix

        user_similarity_profile is a 1x|U| user similarity vector, where each entry corresponds to the similarity between
        the user we are generating recommendations for and a user entry in the ratings_matrix
        """
        scores = user_similarity_profile.dot(self.ratings_matrix.matrix)
        return self.ratings_matrix.normalize_score_vector(scores)


class Group_Recommender():

    def __init__(self, ratings_matrix):
        """
        ratings_matrix is a |U|x|M| matrix composed of prior user ratings
        """
        self.ratings_matrix = ratings_matrix

    def group_recommendation_vector(self, rec_vectors, **kwargs):
        """
        Computes a 1x|M| movie recommendation vector for a group of users using a specified aggregation function,
        given the users individual recommendation vectors.

        rec_vectors is a Recommendations_Vector_Collection
        ratings_matrix is a |U|x|M| matrix composed of prior user ratings

        agg_method is an recommendations aggregation function
            should be either least_misery_aggregation or disagreement_variance_aggregation
        """
        if(len(rec_vectors) == 1):
            return rec_vectors.get_vector(0)

        group_vector = sp.dok_matrix(rec_vectors.get_vector_shape())

        for i in range(group_vector.shape[1]):
            group_vector[0, i] = self.get_agg_method()(rec_vectors.values_at_index(i))

        return group_vector.tocsr()

    def get_agg_method(self):
        return Aggregation_Functions.highest_score_agg


class Least_Misery_Recommender(Group_Recommender):

    def get_agg_method(self):
        return Aggregation_Functions.least_misery_agg


class Disagreement_Variance_Recommender(Group_Recommender):

    def get_agg_method(self):
        return Aggregation_Functions.disagreement_variance_agg


class Recommendations_Vector_Collection:

    @classmethod
    def from_user_ratings(cls, ratings_matrix, user_ratings_list):
        recommender = Recommender(ratings_matrix)

        rvc = Recommendations_Vector_Collection()
        for user_ratings in user_ratings_list:
            if(len(user_ratings) > 0):
                rvc.rec_vectors.append(recommender.single_user_recommendation_vector(user_ratings))

        if(len(rvc) == 0):
            rvc.rec_vectors.append(ratings_matrix.get_top_movies())

        return rvc

    def __init__(self):
        self.rec_vectors = []

    def get_vector(self, i):
        return self.rec_vectors[i]

    def get_vector_shape(self):
        return self.rec_vectors[0].shape

    def values_at_index(self, i):
        return [x[0, i] for x in self.rec_vectors]

    def __len__(self):
        return len(self.rec_vectors)


class Movie_Scores:

    @classmethod
    def from_score_vector(cls, ratings_matrix, score_vec, original_ratings):
        ms = Movie_Scores()

        items = ((ratings_matrix.get_movielens_id(i), score_vec[0, i]) for i in score_vec.indices)
        movielens_items = filter(lambda x: x[0] not in original_ratings, items)
        movielens_items = sorted(movielens_items, key=lambda x: x[1], reverse=True)

        for movie, score in movielens_items:
            ms.add_movie(movie, score)

        return ms

    def __init__(self):
        self.items = OrderedDict()
        self.id_type = "movielens"

    def add_movie(self, movie, score):
        self.items[movie] = score

    def trim_to_top_k(self, quantity):
        trimmed = OrderedDict()

        for i, item in enumerate(self.items.items()):
            if(i >= quantity):
                break

            trimmed[item[0]] = item[1]

        self.items = trimmed

    def filter_on_genres(self, movielens_to_genre, genres):
        if(not genres or len(genres) == 0):
            return

        filtered = OrderedDict()

        for key in self.items.keys():
            if(any(g in movielens_to_genre[key] for g in genres)):
                filtered[key] = self.items[key]

        self.items = filtered

    def filter_on_year(self, movielens_to_year, min_year):
        if(not min_year):
            return

        filtered = OrderedDict()

        for key in self.items.keys():
            if(movielens_to_year[key] >= min_year):
                filtered[key] = self.items[key]

        self.items = filtered

    def convert_indices_to_imdb(self, movie_id_mapper):
        self.id_type = "imdb"
        items = OrderedDict()
        for key, value in self.items.items():
            items[movie_id_mapper[key]] = value
        self.items = items

    def output_as_keys_list(self):
        return list(self.items.keys())

    def output_as_genre_separated_keys_list(self, legal_genres, movielens_to_imdb, 
                                                  movielens_to_genre, movies_per_genre):
        genre_dict = {genre: Movie_Scores() for genre in legal_genres}
        genre_dict["Top"] = Movie_Scores()

        full_genres = {genre: False for genre in legal_genres}

        for i, item in enumerate(self.items.items()):
            if(all(full_genres.values())):
                break

            movie, score = item

            genres = movielens_to_genre[movie]
            genres.add("Top")
            for genre in genres:
                if(len(genre_dict[genre]) >= movies_per_genre):
                    full_genres[genre] = True
                else:
                    genre_dict[genre].add_movie(movie, score)

        for movie_score in genre_dict.values():
            movie_score.convert_indices_to_imdb(movielens_to_imdb)

        return {genre: movie_score.output_as_keys_list() for genre, movie_score in genre_dict.items()}

    def output_as_scores_list(self):
        output = []
        for key, value in self.items.items():
            d = {}
            d[self.id_type] = key
            d["score"] = value
            output.append(d)
        return output

    def __len__(self):
        return len(self.items)
