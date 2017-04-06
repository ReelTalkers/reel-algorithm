import scipy.sparse as sp
from collections import OrderedDict


class Recommender:

    def __init__(self, ratings_matrix):
        """
        ratings_matrix is a |U|x|M| matrix composed of prior user ratings
        """
        self.ratings_matrix = ratings_matrix

    def single_user_recommendation_vector(self, ratings_vector):
        """
        Computes a 1x|M| movie recommendation vector for a given user.
        rating_vector is a 1x|M| sparse vector of user ratings
        """

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

        num_agreements = sum(1 for x in shared_items if abs(user1_preferences[0, x] - user2_preferences[0, x]) <= 2)

        return (num_agreements / len(shared_items) if len(shared_items) > 0 else 0)

    def calculate_item_relevance_scores(self, user_similarity_profile):
        """
        Calculates item relevance scores for each item in the |U|x|M| ratings matrix

        user_similarity_profile is a 1x|U| user similarity vector, where each entry corresponds to the similarity between
        the user we are generating recommendations for and a user entry in the ratings_matrix
        """
        return user_similarity_profile.dot(self.ratings_matrix.matrix) / sum(user_similarity_profile.data)

    def group_recommendation_vector(rec_vectors, agg_method, **kwargs):
        """
        Computes a 1x|M| movie recommendation vector for a group of users using a specified aggregation function,
        given the users individual recommendation vectors.

        rec_vectors is a Recommendations_Vector_Collection
        ratings_matrix is a |U|x|M| matrix composed of prior user ratings

        agg_method is an recommendations aggregation function
            should be either least_misery_aggregation or disagreement_variance_aggregation
        """
        return agg_method(rec_vectors, **kwargs)

    def least_misery_aggregation(rvc, **kwargs):
        group_rec_vector = sp.dok_matrix(rvc.get_vector_shape())

        for i in range(group_rec_vector.shape[1]):
            group_rec_vector[0, i] = rvc.min_at_index(i)

        return group_rec_vector.tocsr()

    def disagreement_variance_aggregation(rvc, **kwargs):
        mean_weight = kwargs.get("mean_weight", .8)

        group_rec_vector = sp.dok_matrix(rvc.get_vector_shape())

        for i in range(group_rec_vector.shape[1]):
            mean, var = rvc.mean_and_var_at_index(i)
            group_rec_vector[0, i] = mean_weight * mean + (1 - mean_weight) * (1 - var)

        return group_rec_vector.tocsr()


class Recommendations_Vector_Collection:

    @classmethod
    def from_user_ratings(cls, ratings_matrix, user_ratings_list, rec_method=single_user_recommendation_vector):
        rvc = Recommendations_Vector_Collection()
        for user_ratings in user_ratings_list:
            rvc.rec_vectors.append(rec_method(ratings_matrix, ratings_matrix.get_ratings_vector(user_ratings)))
        return rvc

    @classmethod
    def from_cached_scores(cls, ratings_matrix, cached_scores_list):
        rvc = Recommendations_Vector_Collection()
        for cached_rec in cached_scores_list:
            rvc.rec_vectors.append(ratings_matrix.get_ratings_vector(cached_rec))
        return rvc

    def __init__(self):
        self.rec_vectors = []

    def get_vector_shape(self):
        return self.rec_vectors[0].shape

    def min_at_index(self, i):
        return min(r[0, i] for r in self.rec_vectors)

    def mean_and_var_at_index(self, i):
        col = [r[0, i] for r in self.rec_vectors]
        mean = sum(col) / len(col)
        var = sum((i - mean) ** 2 for i in col) / len(col)
        return mean, var

    def __add__(self, x):
        self.rec_vectors.extend(x.rec_vectors)
        return self


class Movie_Scores:

    @classmethod
    def from_score_vector(cls, ratings_matrix, score_vec, original_ratings, top_k):
        ms = Movie_Scores()

        items = ((ratings_matrix.get_movielens_id(i), score_vec[0, i]) for i in score_vec.indices)
        movielens_items = filter(lambda x: x[0] not in original_ratings, items)
        movielens_items = sorted(movielens_items, key=lambda x: x[1], reverse=True)[:top_k]

        for movie, score in movielens_items:
            ms.add_movie(movie, score)

        return ms

    def __init__(self):
        self.items = OrderedDict()
        self.id_type = "movielens"

    def add_movie(self, movie, score):
        self.items[movie] = score

    def convert_indices_to_imdb(self, movie_id_mapper):
        self.id_type = "imdb"
        items = OrderedDict()
        for key, value in self.items.items():
            items[movie_id_mapper[key]] = value
        self.items = items

    def output_as_keys_list(self):
        return list(self.items.keys())

    def output_as_scores_list(self):
        output = []
        for key, value in self.items.items():
            d = {}
            d[self.id_type] = key
            d["score"] = value
            output.append(d)
        return output
