def main(zone, cp, ds, mindis, fl, yp=None, yn=None):
    """
    Update bike distribution according to repositioning results (if any) and users move.

    Parameters
    ----------
    yp: array, dtype=float, size=zone
        total number of bikes picked up from each station according to repositioning policy

    yn: array, dtype=float, size=zone
        total number of bikes dropped off at each station according to repositioning policy

    ...

    Returns
    ----------
    ds: array, dtype=float, size=zone
        updated bike distribution
    """

    # Apply redeployment if any
    if (yp and yn):
        for s in range(zone):
            ds[s] = ds[s] - yp[s] + yn[s]

    dsold = ds.copy()

    # Bikes leave
    for s in range(zone):
        ds[s] -= min(dsold[s], sum(fl[s]))
    
    # Bikes return
    for s in range(zone):
        for z in range(zone):
            if sum(fl[z]) > 0:
                ds[s] += fl[z][s] * min(dsold[z], sum(fl[z])) / sum(fl[z])
    
    # Check against station capacity
    for s in range(zone):
        if ds[s] > cp[s]:
            exceed = ds[s] - cp[s]
            ds[s] = cp[s]
            # loop over stations in min distance order
            for i in mindis[s]:
                space = cp[i] - ds[i]
                # if station i can take all exceed
                if exceed <= space:
                    ds[i] += exceed
                    break
                # if station i can take some but not all exceed
                elif space > 0 and space < exceed:
                    ds[i] = cp[i]
                    exceed -= space

    return ds
