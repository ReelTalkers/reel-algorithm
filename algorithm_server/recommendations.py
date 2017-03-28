import scipy.sparse as sp
from collections import OrderedDict
from itertools import islice


def group_recommendation_vector(ratings_matrix, user_ratings_list, agg_method, **kwargs):
    """
    Computes a 1x|M| movie recommendation vector for a group of users using a specified aggregation function.
    Does not consider any cached movie recommendations.

    ratings_matrix is a |U|x|M| matrix composed of prior user ratings
    user_ratings_list is a list of dictionaries, one dictionary for each user that is part of the group
        Each dictionary maps (movielens_id) -> (user rating) for that particular user

    agg_method is an recommendations aggregation function
        should be either least_misery_aggregation or disagreement_variance_aggregation
    """
    return agg_method([single_user_recommendation_vector(ratings_matrix, u) for u in user_ratings_list], **kwargs)


def group_recommendation_vector_from_cache(ratings_matrix, user_ratings_list, cached_vectors, agg_method, **kwargs):
    """
    Computes a 1x|M| movie recommendation vector for a group of users using a specified aggregation function.
    Considers any cached movie recommendations.

    ratings_matrix is a |U|x|M| matrix composed of prior user ratings
    user_ratings_list is a list of dictionaries, one dictionary for each user that is part of the group
        Each dictionary maps (movielens_id) -> (user rating) for that particular user

    cached_vectors is a list of cached movie recommendation vectors.

    agg_method is an recommendations aggregation function
        should be either least_misery_aggregation or disagreement_variance_aggregation
    """

    rec_vectors = [single_user_recommendation_vector(ratings_matrix, u) for u in user_ratings_list]
    rec_vectors.extend(cached_vectors)

    return agg_method(rec_vectors, **kwargs)


def single_user_recommendation_vector(ratings_matrix, new_user_ratings):
    """
    Computes a 1x|M| movie recommendation vector for a given user.

    ratings_matrix is a |U|x|M| matrix composed of prior user ratings
    new_user_ratings is a dictionary mapping (movielens id) -> (user rating)
        for the user we are generating recommendations for
    """

    user_similarity_profile = calculate_user_similarity_profile(ratings_matrix, new_user_ratings)

    return calculate_item_relevance_scores(ratings_matrix, user_similarity_profile)


def least_misery_aggregation(rec_vectors, **kwargs):
    group_rec_vector = sp.dok_matrix(rec_vectors[0].shape)

    for i in range(group_rec_vector.shape[1]):
        group_rec_vector[0, i] = min(r[0, i] for r in rec_vectors)

    return group_rec_vector.tocsr()


def disagreement_variance_aggregation(rec_vectors, **kwargs):
    mean_weight = kwargs.get("mean_weight", .8)

    group_rec_vector = sp.dok_matrix(rec_vectors[0].shape)

    for i in range(group_rec_vector.shape[1]):
        col = [r[0, i] for r in rec_vectors]
        mean = sum(col) / len(col)
        var = sum((i - mean) ** 2 for i in col) / len(col)
        group_rec_vector[0, i] = mean_weight * mean + (1 - mean_weight) * (1 - var)

    return group_rec_vector.tocsr()


def calculate_user_similarity_profile(ratings_matrix, new_user_ratings):
    """
    ratings_matrix is a |U|x|M| matrix composed of prior user ratings

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


def get_movie_scores(ratings_matrix, item_scores, original_ratings, top_k):
    """
    Returns an ordered dictionary containing the top-k higest scoring items in item_scores,
    with the indices in item_scores converted to movie lens ids using the ratings matrix
    """

    movielens_items = ((ratings_matrix.get_movielens_id(i), item_scores[0, i]) for i in item_scores.indices)
    movielens_items = filter(lambda x: x[0] not in original_ratings, movielens_items)
    movielens_items = sorted(movielens_items, key=lambda x: x[1], reverse=True)[:top_k]

    indexed_items = OrderedDict()
    for movie, score in movielens_items:
        indexed_items[movie] = score

    return indexed_items
