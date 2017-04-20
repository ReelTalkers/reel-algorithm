
ORIGDIR = "data/movielens/ml-latest-small"
SAVEDIR_BASE = "data/movielens/ml-"

def get_ratings_per_user(datadir):
    ratings_per_user = {}
    reader = open("%s/ratings.csv" % datadir)
    for line in reader.readlines():
        fields = line.split(",")
        uid = fields[0]
        ratings_per_user[uid] = ratings_per_user.get(uid, 0) + 1
    reader.close()
    del(ratings_per_user["userId"])
    return ratings_per_user


def trim_dataset(num_ratings):
    return None


if __name__ == "__main__":
    print(get_ratings_per_user(ORIGDIR))