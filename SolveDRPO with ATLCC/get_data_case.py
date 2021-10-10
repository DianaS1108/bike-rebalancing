def main(input_scenario, htime, zone):
    """
    Read case data in rebalancing problem.

    Returns
    ----------
    ds: array, type=int, size=zone
        initial bike distributions
    
    orig_fl: array, type=float, size=htime*zone*zone
        demand flows in input scenario
    """

    # ds
    ds = [0 for s in range(zone)]
    # read from dataset

    # Flow of input scenario
    orig_fl = [[[0.0 for i in range(zone)] for j in range(zone)]for t in range(htime)]
    # read from dataset

    return ds, orig_fl
