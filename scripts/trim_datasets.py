import argparse
from shutil import copyfile
import os

def ratings_file(datadir):
    return "%s/ratings.csv" % datadir

def links_file(datadir):
    return "%s/links.csv" % datadir

def movies_file(datadir):
    return "%s/movies.csv" % datadir

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


def trim_dataset(origdir, savedir, num_ratings):
    try:
        os.mkdir(savedir)
    except:
        print("Directory already exists")

    ratings_per_user = get_ratings_per_user(origdir)
    users_to_keep = get_users_to_keep(ratings_per_user, num_ratings)

    reader = open("%s/ratings.csv" % origdir, "r")
    writer = open("%s/ratings.csv" % savedir, "w")

    writer.write(reader.readline())

    for line in reader.readlines():
        fields = line.split(",")
        if fields[0] in users_to_keep:
            writer.write(line)

    reader.close()
    writer.close()

    copyfile(links_file(origdir), links_file(savedir))
    copyfile(movies_file(origdir), movies_file(savedir))

    

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
    parser = argparse.ArgumentParser()
    parser.add_argument('--datadir', type=str, help='Original data directory of movielens dataset.')
    parser.add_argument('--savedir_base', type=str, help='Location to save new data directories.')
    parser.add_argument('--base_num_ratings', type=int, help='Number of base ratings to keep')
    parser.add_argument('--max_ratings_multiplier', type=int, help='Max multiplier for base_num_ratings')

    parser.set_defaults(datadir="data/movielens/ml-latest-small", savedir_base="data/movielens/ml",
                        base_num_ratings=100000, max_ratings_multiplier=10)

    args = parser.parse_args()

    for i in range(1, args.max_ratings_multiplier + 1):
        num_ratings = i * args.base_num_ratings
        savedir = "%s-%d" % (args.savedir_base, num_ratings)

        print("Now generating: %s" % savedir)

        trim_dataset(args.datadir, savedir, num_ratings)
