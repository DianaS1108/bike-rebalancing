def modify_cluster(cluster, assignment, centre, zone, cp, ds, mindis, trainsample, train_fl):
    """
    Modify clusters based on demands flow

    Returns
    ----------
    assignment: array, dtype=int, size=zone
        updated assignment of each station to cluster
    """

    from modify_cluster.compute_orig_loss import compute_orig_loss
    from modify_cluster.compute_average_loss import compute_average_loss

    # Compute original loss
    loss = compute_orig_loss(zone, cp, ds, trainsample, train_fl)

    # Compute ALg
    AL = compute_average_loss(loss)
    
    ALc = [0 for c in range(cluster)]

    # Compute ALc and try capping it by kicking out one station if needed
    for c in range(cluster):
        
        # Compute ALc
        ALc[c] = compute_average_loss(
            [[loss[ts][s] for s in range(zone) if assignment[s] == c] for ts in range(trainsample)]
        )

        # Try kicking out one station if needed
        if ALc[c] > AL:
            for s in reversed(mindis[centre[c]]):
                if (assignment[s] == c):

                    tmp = compute_average_loss(
                    [[loss[ts][z] for z in range(zone) if (assignment[z] == c and z != s)] for ts in range(trainsample)]
                    )

                    if tmp <= AL and s != centre[c]:
                        assignment[s] = -1
                        ALc[c] = tmp
                        break

    # Assign outliers
    # Try assigning to cluster without breaking ALg
    for s in range(zone):
        if assignment[s] == -1:
            for c in sorted(range(cluster), key=lambda x: ALc[x]):
                tmp = compute_average_loss(
                    [[loss[ts][z] for z in range(zone) if (assignment[z] == c or z == s)] for ts in range(trainsample)]
                )
                if tmp <= AL:
                    assignment[s] = c
                    ALc[c] = tmp
                    break
    
    # Assign remaining outliers to cluster with lowest ALc
    for s in range(zone):
        if assignment[s] == -1:
            current_min = sorted(range(cluster), key=lambda x: ALc[x])[0]
            assignment[s] = current_min
            ALc[current_min] = compute_average_loss(
                [[loss[ts][z] for z in range(zone) if assignment[z] == current_min] for ts in range(trainsample)]
            )
        
    return assignment
