def compute_orig_loss(zone, cp, orig_ds, trainsample, train_fl):
    """
    Compute original loss at each station in each training scenario.

    Returns
    ------
    loss: array, dtype=float, size = trainsample*zone
        original total loss at each station in each training scenario
    """

    # Initialize losses
    loss_bike = [[0.0 for i in range(zone)] for ts in range(trainsample)]
    loss_dock = [[0.0 for i in range(zone)] for ts in range(trainsample)]
    loss = [[0.0 for i in range(zone)] for ts in range(trainsample)]

    # Compute total demand flows in and out of each station
    train_fl_out = [[sum(train_fl[ts][s]) for s in range(zone)] for ts in range(trainsample)]

    # Compute losses
    for ts in range(trainsample):

        ds = orig_ds.copy()

        for s in range(zone):
            # Loss bike
            loss_bike[ts][s] = max(train_fl_out[ts][s] - ds[s], 0)

            # Bikes leave
            ds[s] -= min(ds[s], train_fl_out[ts][s])
        
        # Bikes return
        for s in range(zone):
            for z in range(zone):
                if train_fl_out[ts][z] > 0:
                    ds[s] += train_fl[ts][z][s] * min(ds[z], train_fl_out[ts][z]) / train_fl_out[ts][z]

        # Loss dock
        for s in range(zone):
            loss_dock[ts][s] = max(ds[s] - cp[s], 0)
        
        # Total loss
        for s in range(zone):
            loss[ts][s] = loss_bike[ts][s] + loss_dock[ts][s]
    
    return loss
