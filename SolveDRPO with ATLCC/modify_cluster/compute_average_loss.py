def compute_average_loss(loss):
    """
    Compute average loss over stations of non-zero loss over different scenarios.

    Parameters
    ----------
    loss: array, dtype=float, size = trainsample*zone
        loss at each station in each scenario
    
    Returns
    ------
    AL: float
        average loss over stations of non-zero loss over different scenarios.
    """

    trainsample = len(loss)
    zone = len(loss[0])

    loss_sum = 0

    for ts in range(trainsample):

        loss_ts_sum = 0
        loss_ts_count = 0

        for s in range(zone):
            if loss[ts][s] > 0:
                loss_ts_sum += loss[ts][s]
                loss_ts_count += 1
        
        if loss_ts_count > 0:
            loss_sum += loss_ts_sum / loss_ts_count

    return loss_sum / trainsample
