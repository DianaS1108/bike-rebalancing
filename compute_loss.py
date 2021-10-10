def main(scenario, htime, zone, yp, yn):
    """
    Compute total loss in a system under given scenario with given rebalancing policy.

    Returns
    ----------
    total loss: array, dtype=float, size=htime
        total loss in the system at each timestep
    """

    # Read data
    cp = [0 for s in range(zone)]
    # read from dataset

    ds = [[0 for s in range(zone)] for t in range(htime + 1)]
    # read from dataset

    fl = [[[0.0 for z in range(zone)] for s in range(zone)] for t in range(htime)]
    tfl = [[0.0 for s in range(zone)]for t in range(htime)]  # total flow out
    # read from dataset

    xfl = [[[0.0 for z in range(zone)] for s in range(zone)] for t in range(htime)]  # initialize actual flow

    dis = [[0.0 for z in range(zone)] for s in range(zone)]
    # read from dataset

    mindis = [[0 for z in range(zone)] for s in range(zone)]
    for s in range(zone):
        sortindex = sorted(range(zone), key=lambda x: dis[s][x])
        mindis[s] = sortindex
    
    loss = [[0 for t in range(htime)] for i in range(3)]

    # Run
    for t in range(htime):

        # Apply redeployment
        for s in range(zone):
            ds[t][s] = ds[t][s] - yp[t][s] + yn[t][s]

        # Compute actual flow
        for s in range(zone):
            if tfl[t][s] > 0:
                for z in range(zone):
                    xfl[t][s][z] = fl[t][s][z] * min(ds[t][s], tfl[t][s]) / tfl[t][s]

                    # Compute loss demand
                    loss[0][t] += fl[t][s][z] - xfl[t][s][z]

        # Bikes leave
        for s in range(zone):
            ds[t+1][s] = ds[t][s] - min(ds[t][s], tfl[t][s])

        # Bikes return
        for s in range(zone):
            for z in range(zone):
                ds[t+1][s] += xfl[t][z][s]

        # Check against station capacity
        for s in range(zone):
            # If station s is overload
            if ds[t+1][s] > cp[s]:
                exceed = ds[t+1][s] - cp[s]
                ds[t+1][s] = cp[s]
                loss[1][t] += exceed

                # loop over stations in min distance order
                for z in mindis[s]:
                    space = cp[z] - ds[t+1][z]

                    # if station z can take all exceed
                    if exceed <= space:
                        ds[t+1][z] += exceed
                        break

                    # if station z can take some but not all exceed
                    elif space > 0 and space < exceed:
                        #loss[reb][1][t] += (exceed - space)
                        exceed -= space
                        ds[t+1][z] = cp[z]

            # Total loss
            loss[2][t] = loss[0][t] + loss[1][t]

    return loss[2]
