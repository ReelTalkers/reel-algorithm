import io_utils
import scipy.sparse as sp
import sklearn.metrics as sk


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


def get_top_movielens_ids(ratings_matrix, item_scores, original_ratings, top_k=100):
    """
    Returns an ordered dictionary containing the top-k higest scoring items in item_scores,
    with the indices in item_scores converted to movie lens ids using the ratings matrix
    """

    movielens_items = ((ratings_matrix.get_movielens_id(i), item_scores[0, i]) for i in item_scores.indices)
    movielens_items = filter(lambda x: x[0] not in original_ratings, movielens_items)
    items = sorted(movielens_items, key=lambda x: x[1], reverse=True)

    return [x[0] for x in items[:top_k]]


def get_top_movielens_titles(movie_title_dict, top_movielens_ids):
    return [movie_title_dict[x] for x in top_movielens_ids]


def get_top_movie_titles(ratings_file, datadir):
    ratings_matrix = io_utils.build_user_item_matrix(datadir)

    new_user_ratings = io_utils.get_sample_ratings_dict(datadir, ratings_file)

    user_similarity_profile = calculate_user_similarity_profile(ratings_matrix, new_user_ratings)

    relevance_scores = calculate_item_relevance_scores(ratings_matrix, user_similarity_profile)

    top_movielens_ids = get_top_movielens_ids(ratings_matrix, relevance_scores, new_user_ratings.keys())

    return get_top_movielens_titles(io_utils.get_movie_id_title_dict(datadir), top_movielens_ids)


if __name__ == "__main__":
    ratings_files = ["data/sample_users/andrew.txt", "data/sample_users/galen.txt"]
    datadir = "data/small"

    top_titles = [get_top_movie_titles(r, datadir) for r in ratings_files]

    print(sk.jaccard_similarity_score(top_titles[0], top_titles[1]))
