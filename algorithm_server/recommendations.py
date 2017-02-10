import io_utils
import scipy.sparse as sp
import sklearn.preprocessing as sk
import numpy as np


def calculate_user_similarities(ratings_matrix, new_user_reviews):
    num_users = ratings_matrix.shape[0]

    user_similarities = np.array()
    for i in range(num_users):

        row = ratings_matrix.getrow(i)
        print(type(row))

    return user_similarities
