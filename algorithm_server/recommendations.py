import io_utils
import scipy.sparse as sp


def calculate_user_similarity_profile(ratings_matrix, new_user_reviews):
    """
    ratings_matrix is a |U|x|M| sparse matrix

    new_user_reviews is a dictionary that maps (movielens id) -> (user rating)

    We want to return a 1x|U| dense user similiarity vector

    """
    num_users, num_movies = ratings_matrix.get_shape()

    #Converts the user reviews dictionary to a 1x|M| vector
    #of user reviews with the same indices as the ratings matrix
    vector_user_reviews = ratings_matrix.get_ratings_vector(new_user_reviews)

    user_similarities = sp.dok_matrix((1, num_users))
    for i in range(num_users):

        user_similarities[0, i] = calculate_pairwise_user_similarity(ratings_matrix.getrow(i), vector_user_reviews)

    return user_similarities.tocsr()


def calculate_pairwise_user_similarity(user1_preferences, user2_preferences):
    """
    Both user preferences parameters are sparse 1x|M| vectors corresponding to movie ratings

    """

    shared_items = set(user1_preferences.indices) & set(user2_preferences.indices)

    num_agreements = sum(1 for x in shared_items if abs(user1_preferences[0, x] - user2_preferences[0, x]) <= 2)

    return (num_agreements / len(shared_items) if len(shared_items) > 0 else 0)


def calculate_item_relevance_scores(ratings_matrix, user_similarity_profile):
    return user_similarity_profile.dot(ratings_matrix.matrix) / sum(user_similarity_profile.data)


def convert_item_scores_to_movielens_ids(rating_matrix, item_scores):
    return None


if __name__ == "__main__":
    datadir = "../data/small"

    ratings_matrix = io_utils.build_user_item_matrix(datadir)

    new_user_ratings = io_utils.get_first_user_rating_dict(datadir)

    user_similarity_profile = calculate_user_similarity_profile(ratings_matrix, new_user_ratings)

    relevance_scores = calculate_item_relevance_scores(ratings_matrix, user_similarity_profile)

    print(relevance_scores)
