def initialize_location(zone, vec):
    """
    Initialize location of operators as uniform distribution.
    Replace this function for other types of operator initial distribution.

    Returns
    ----------
    location: array, dtype=int, size=vec*zone
        indicator variables for operator locations
    """

    location = [[0 for j in range(zone)] for i in range(vec)]

    xx = zone // vec
    for i in range(vec):
        for j in range(zone):
            if j == xx * i:
                location[i][j] = 1
            else:
                location[i][j] = 0  # evenly distributed
    
    return location
