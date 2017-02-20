import io_utils
import scipy.sparse as sp
from collections import *
from itertools import *


def single_user_recommendation_vector(ratings_matrix, new_user_ratings):

    user_similarity_profile = calculate_user_similarity_profile(ratings_matrix, new_user_ratings)

    return calculate_item_relevance_scores(ratings_matrix, user_similarity_profile)


def calculate_user_similarity_profile(ratings_matrix, new_user_ratings):
    """
    ratings_matrix is a |U|x|M| sparse matrix

    new_user_ratings is a dictionary that maps (movielens id) -> (user rating)

    We want to return a 1x|U| dense user similiarity vector

    """
    num_users, num_movies = ratings_matrix.get_shape()

    #Converts the user reviews dictionary to a 1x|M| vector
    #of user ratings with the same indices as the ratings matrix
    vector_user_ratings = ratings_matrix.get_ratings_vector(new_user_ratings)

    user_similarities = sp.dok_matrix((1, num_users))
    for i in range(num_users):

        user_similarities[0, i] = calculate_pairwise_user_similarity(ratings_matrix.getrow(i), vector_user_ratings)

    return user_similarities.tocsr()


def calculate_pairwise_user_similarity(user1_preferences, user2_preferences):
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


def calculate_item_relevance_scores(ratings_matrix, user_similarity_profile):
    """
    Calculates item relevance scores for each item in the |U|x|M| ratings matrix

    user_similarity_profile is a 1x|U| user similarity vector, where each entry corresponds to the similarity between
    the user we are generating recommendations for and a user entry in the ratings_matrix
    """
    return user_similarity_profile.dot(ratings_matrix.matrix) / sum(user_similarity_profile.data)


def get_ranked_movielens_ids(ratings_matrix, item_scores, original_ratings):
    """
    Returns an ordered dictionary containing the top-k higest scoring items in item_scores,
    with the indices in item_scores converted to movie lens ids using the ratings matrix
    """

    movielens_items = ((ratings_matrix.get_movielens_id(i), item_scores[0, i]) for i in item_scores.indices)
    movielens_items = filter(lambda x: x[0] not in original_ratings, movielens_items)
    movielens_items = sorted(movielens_items, key=lambda x: x[1], reverse=True)

    indexed_items = OrderedDict()
    for movie, score in movielens_items:
        indexed_items[movie] = score

    return indexed_items


def get_top_k_movielens_ids(ranked_movielens_ids, top_k):
    """
    ranked_movielens_ids is an OrderedDict mapping (movielens_id) -> (score) with monotonically decreasing scores
    Typically obtained through the get_ranked_movielens_ids() function

    Returns a list of the top-k movielens ids from this collection
    """
    return list(islice(ranked_movielens_ids, top_k))


def get_ranked_movielens_ids_from_file(ratings_file, datadir, top_k=None):
    """
    Gets an OrderedDict mapping (movielens_id) -> (score) with monotonically decreasing scores

    ratings_file is the filepath of a text file containing (imdb id) -> (rating) pairs
    datadir is the filepath of a directory containing all movie data

    """
    ratings_matrix = io_utils.build_user_item_matrix(datadir)

    new_user_ratings = io_utils.get_sample_ratings_dict(datadir, ratings_file)

    relevance_scores = single_user_recommendation_vector(ratings_matrix, new_user_ratings)

    return get_ranked_movielens_ids(ratings_matrix, relevance_scores, new_user_ratings.keys())


if __name__ == "__main__":
    ratings_files = ["data/sample_users/andrew.txt", "data/sample_users/galen.txt"]
    datadir = "data/movielens/ml-latest-small"

    print(get_top_k_movielens_ids(get_ranked_movielens_ids_from_file(ratings_files[0], datadir)))
