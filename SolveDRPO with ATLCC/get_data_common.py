def main(htime, zone, trainsample):
    """Read common data in rebalancing problem.

    Returns
    ----------
    cp: array, dtype=int, size=zone
        station capacity

    dis: array, dtype=float, size=zone*zone
        distance between stations

    mindis: array, dtype=int, size=zone*zone
        for each station, stations in ascending order of distance

    fl: array, dtype=float, size=trainsample*htime*zone*zone
        demand flows in training scenarios
    """

    # Station capacity
    cp = [0 for s in range(zone)]
    # read from dataset

    # Distance between stations
    dis = [[0.0 for j in range(zone)] for i in range(zone)]
    # read from dataset

    # For each station, rank of all stations in min distance order
    mindis = [[0 for i in range(zone)] for s in range(zone)]

    for s in range(zone):
        sortindex = sorted(range(zone), key=lambda x: dis[s][x])
        mindis[s] = sortindex

    # Training flow
    fl = [
        [[[0.0 for j in range(zone)] for i in range(zone)] for t in range(htime)]
        for ts in range(trainsample)
    ]
    # read from dataset

    return cp, dis, mindis, fl
