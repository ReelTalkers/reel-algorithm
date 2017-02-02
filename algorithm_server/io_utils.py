
def get_ratings_stream(filename):
    reader = open(filename, "r")
    for i, line in enumerate(reader.readlines()):
        if(i >= 1):
            yield tuple(str(line).strip().split(",")[:3])
    reader.close()


def map_movie_id_to_matrix_location(filename):
    matrix_loc_map = dict()

    reader = open(filename, "r")
    for i, line in enumerate(reader.readlines()):
        if(i >= 1):
            comma_pos = line.find(",")
            if(comma_pos > 0):
                matrix_loc_map[line[:comma_pos]] = i

    return matrix_loc_map
