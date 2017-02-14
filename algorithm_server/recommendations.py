import io_utils
import scipy.sparse as sp
import numpy as np
import math


def calculate_all_user_similarities(ratings_matrix, new_user_reviews):
    """
    ratings_matrix is a |U|x|M| sparse matrix

    new_user_reviews is a dictionary that maps (movielens id) -> (user rating)

    We want to return a 1x|U| dense user similiarity vector

    """
    num_users, num_movies = ratings_matrix.get_shape()

    user_similarities = sp.dok_matrix((1, num_users))
    for i in range(num_users):

        row = ratings_matrix.getrow(i)
        print(type(row))

    return user_similarities


def calculate_pairwise_user_similarity(user1_preferences, user2_preferences):
    """
    Both user preferences parameters are sparse 1x|M| vectors corresponding to movie ratings

    """

    shared_items = set(user1_preferences.indices) & set(user2_preferences.indices)

    num_agreements = sum(1 for x in shared_items if abs(user1_preferences[0, x] - user2_preferences[0, x]) < 2)

    return (num_agreements / len(shared_items) if len(shared_items) > 0 else 0)


if __name__ == "__main__":
    m = io_utils.build_user_item_matrix("../data-small")

    for x in range(m.matrix.get_shape()[0]):
        print(calculate_pairwise_user_similarity(m.getrow(0), m.getrow(x)))
