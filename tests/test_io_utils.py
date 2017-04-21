from algorithm_server import io_utils as io_utils

datadir = "data/movielens/ml-latest-small"

def test_release_year_mapping():
	year_mapping = io_utils.get_year_mapping(datadir)

	assert all(type(y) == int for y in year_mapping.values())
	assert all(y in range(1800, 2100) for y in year_mapping.values())
