import argparse
import algorithm_server.app as app

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--datadir', type=str, help='Data directory of movielens dataset.')

    parser.set_defaults(datadir="data/movielens/ml-latest-small")

    args = parser.parse_args()

    datadir = args.datadir
    app.start_server(datadir)
