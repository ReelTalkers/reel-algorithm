from shutil import copyfile

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


def trim_dataset(origdir, savdir, num_ratings):
    ratings_per_user = get_ratings_per_user(origdir)

    

def get_users_to_keep(ratings_per_user, num_ratings):
    users_to_keep = set()
    curr_ratings = 0

    for user in sorted(ratings_per_user.keys(), key=lambda x: ratings_per_user[x], reverse=True):
        if(curr_ratings > num_ratings):
            break

        users_to_keep.add(user)
        curr_ratings += ratings_per_user[user]

    return users_to_keep


if __name__ == "__main__":
    ORIGDIR = "data/movielens/ml-latest-small"
    SAVEDIR_BASE = "data/movielens/ml"

    for i in range(1, 5):
        trim_dataset(ORIGDIR, "%s-%d" % (SAVEDIR_BASE, i), i)
