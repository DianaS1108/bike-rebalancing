def initialize_cluster(cluster, zone, mindis):
    """
    Initialize clusters with uniformly chosen centres and distance basis.

    Parameters
    ----------
    cluster: int
        cluster number
    ...

    Returns
    ----------
    assignment: array, dtype=int, size=zone
        cluster assignment for each station
    
    centre: array, dtype=int, size=cluster
        centre station for each cluster
    """

    # Initialize cluster centre
    centre = [i * (zone // cluster) for i in range(cluster)]  # uniform dis

    # Assign all stations according to distance
    assignment = [-1 for i in range(zone)]
    for s in range(zone):
        for z in mindis[s]:
            if z in centre:
                assignment[s] = centre.index(z)
                break

    return assignment, centre
