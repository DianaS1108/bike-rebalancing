def main(zone, cp, ds, vec, cap, location, dis, trainsample, train_fl_out, train_fl_in, dismaxpick, dismaxdrop):
    """
    Generate repositioning policy by optimization.
    If no solution exists, no repositioning is performed.

    Returns
    ----------
    status: int
        indicate the status of solving optimization problem
        0 if solution exists, 1 otherwise

    yp_total: array, dtype=float, size=zone
        total number of bikes picked up from each station ub repositioning policy

    yn_total: array, dtype=float, size=zone
        total number of bikes dropped off at each station according to repositioning policy

    bn: array, dtype=int, size=vec*zone
        indicate drop-off station of each operator
    """

    import cplex
    from cplex.exceptions.errors import CplexSolverError

    # Set of near stations for each station
    nearstation = {}
    for s in range(zone):
        nearstation[s] = []
        for z in range(zone):
            if (s != z) and (dis[s][z] <= dismaxpick):
                nearstation[s].append(z)

    # Pickuprange: set of near stations for each operator
    pickuprange = {}
    for v in range(vec):
        for s in range(zone):
            if location[v][s] == 1:
                initial_location = s
                break
        pickuprange[v] = nearstation[initial_location]

    # Initialize optimization problem
    prob = cplex.Cplex()

    prob.set_log_stream(None)
    prob.set_error_stream(None)
    prob.set_warning_stream(None)
    #prob.set_results_stream(None)

    prob.parameters.lpmethod.set(prob.parameters.lpmethod.values.network)
    prob.parameters.emphasis.memory.set(1)
    prob.parameters.mip.strategy.nodeselect.set(0)
    prob.parameters.timelimit.set(600)

    prob.objective.set_sense(prob.objective.sense.minimize)

    # Add constrains

    sense1 = "G" * trainsample * zone
    row1 = [0 for i in range(trainsample * zone)]
    rowname1 = ["" for i in range(trainsample * zone)]

    senseA = "G" * trainsample * zone
    rowA = [0 for i in range(trainsample * zone)]
    rownameA = ["" for i in range(trainsample * zone)]

    sense2 = "L" * zone * vec
    row2 = [0 for i in range(zone * vec)]
    rowname2 = ["" for i in range(zone * vec)]

    sense9 = "L" * zone
    row9 = [0 for i in range(zone)]
    rowname9 = ["" for i in range(zone)]

    sense3 = "L" * zone
    row3 = [0 for i in range(zone)]
    rowname3 = ["" for i in range(zone)]

    sense41 = "L" * zone * vec
    row41 = [0 for i in range(zone * vec)]
    rowname41 = ["" for i in range(zone * vec)]

    sense42 = "L" * zone * vec
    row42 = [0 for i in range(zone * vec)]
    rowname42 = ["" for i in range(zone * vec)]

    sense43 = "L" * zone * vec
    row43 = [0 for i in range(zone * vec)]
    rowname43 = ["" for i in range(zone * vec)]

    sense5 = "L" * vec * zone * zone
    row5 = [0 for i in range(zone * zone * vec)]
    rowname5 = ["" for i in range(zone * zone * vec)]

    sense6 = "E" * vec
    row6 = [0 for i in range(vec)]
    rowname6 = ["" for i in range(vec)]

    sense7 = "E" * vec
    row7 = [0 for i in range(vec)]
    rowname7 = ["" for i in range(vec)]

    sense8 = "E" * vec
    row8 = [0 for i in range(vec)]
    rowname8 = ["" for i in range(vec)]

    for ts in range(trainsample):
        for s in range(zone):
            n = ts * zone + s

            row1[n] = train_fl_out[ts][s] - ds[s]
            rowname1[n] = "c01" + str(n)

            rowA[n] = train_fl_in[ts][s] + ds[s] - cp[s]
            rownameA[n] = "c0A" + str(n)

    for v in range(vec):
        for s in range(zone):
            n = v * zone + s

            row2[n] = 0
            rowname2[n] = "c02" + str(n)

            row41[n] = 0
            rowname41[n] = "c41" + str(n)

            row42[n] = 0
            rowname42[n] = "c42" + str(n)

            row43[n] = cap[v]
            rowname43[n] = "c43" + str(n)

    for s in range(zone):
        row9[s] = ds[s]
        rowname9[s] = "c09" + str(s)

        row3[s] = cp[s] - ds[s]
        rowname3[s] = "c03" + str(s)

    for v in range(vec):
        for s1 in range(zone):
            for s2 in range(zone):
                n = v * zone * zone + s1 * zone + s2
                row5[n] = dis[s1][s2] + dismaxdrop
                rowname5[n] = "c05" + str(n)

    for v in range(vec):
        row6[v] = 1
        rowname6[v] = "c06" + str(v)

        row7[v] = 1
        rowname7[v] = "c07" + str(v)

        row8[v] = 0
        rowname8[v] = "c08" + str(v)

    prob.linear_constraints.add(rhs=row1, senses=sense1, names=rowname1)
    prob.linear_constraints.add(rhs=rowA, senses=senseA, names=rownameA)
    prob.linear_constraints.add(rhs=row2, senses=sense2, names=rowname2)
    prob.linear_constraints.add(rhs=row9, senses=sense9, names=rowname9)
    prob.linear_constraints.add(rhs=row3, senses=sense3, names=rowname3)
    prob.linear_constraints.add(rhs=row41, senses=sense41, names=rowname41)
    prob.linear_constraints.add(rhs=row42, senses=sense42, names=rowname42)
    prob.linear_constraints.add(rhs=row43, senses=sense43, names=rowname43)
    prob.linear_constraints.add(rhs=row5, senses=sense5, names=rowname5)
    prob.linear_constraints.add(rhs=row6, senses=sense6, names=rowname6)
    prob.linear_constraints.add(rhs=row7, senses=sense7, names=rowname7)
    prob.linear_constraints.add(rhs=row8, senses=sense8, names=rowname8)

    print("Constrains added.")

    # Add variables
    # L
    for ts in range(trainsample):
        for s in range(zone):
            n = ts * zone + s
            col = [[[rowname1[n]], [1]]]
            prob.variables.add(
                obj=[1],
                ub=[100], lb=[0],
                #types="I",
                columns=col,
                names=["L" + str(n)]
            )

    print("L added.")

    # LB
    for ts in range(trainsample):
        for s in range(zone):
            n = ts * zone + s
            col = [[[rownameA[n]], [1]]]
            prob.variables.add(
                obj=[1],
                ub=[100], lb=[0],
                columns=col,
                names=["LB" + str(n)]
            )
    
    print("LB added.")

    # yp
    for v in range(vec):
        for s in range(zone):
            n = v * zone + s

            col = [[[], []]]

            for ts in range(trainsample):
                col[0][0].append(rowname1[ts * zone + s])
                col[0][1].append(-1)

                col[0][0].append(rownameA[ts * zone + s])
                col[0][1].append(1)

            col[0][0].append(rowname2[n])
            col[0][1].append(1)

            col[0][0].append(rowname9[s])
            col[0][1].append(1)

            for z in range(zone):
                m = v * zone + z

                col[0][0].append(rowname42[m])
                col[0][1].append(-1)

                col[0][0].append(rowname43[m])
                col[0][1].append(1)

            prob.variables.add(
                obj=[0],
                ub=[cap[v]], lb=[0],
                #types="I",
                columns=col,
                names=["yp" + str(n)]
            )

    print("yp added.")

    # yn
    for v in range(vec):
        for s in range(zone):
            n = v * zone + s

            col = [[[], []]]

            for ts in range(trainsample):
                col[0][0].append(rowname1[ts * zone + s])
                col[0][1].append(1)

                col[0][0].append(rownameA[ts * zone + s])
                col[0][1].append(-1)

            col[0][0].append(rowname3[s])
            col[0][1].append(1)

            col[0][0].append(rowname41[n])
            col[0][1].append(1)

            col[0][0].append(rowname42[n])
            col[0][1].append(1)

            col[0][0].append(rowname43[n])
            col[0][1].append(-1)

            prob.variables.add(
                obj=[0],
                ub=[cap[v]], lb=[0],
                #types="I",
                columns=col,
                names=["yn" + str(n)]
            )

    print("yn added.")

    # bp
    for v in range(vec):
        for s in range(zone):
            n = v * zone + s

            col = [[[], []]]

            col[0][0].append(rowname2[n])
            col[0][1].append(-1 * min(ds[s], cap[v]))

            for z in range(zone):
                col[0][0].append(rowname5[v * zone * zone + s * zone + z])
                col[0][1].append(1 * dis[s][z])

            col[0][0].append(rowname7[v])
            col[0][1].append(1)

            if (s not in pickuprange[v]):
                col[0][0].append(rowname8[v])
                col[0][1].append(1)

            prob.variables.add(
                obj=[0],
                ub=[2], lb=[0],
                types="B",  # binary
                columns=col,
                names=["bp" + str(n)]
            )

    print("bp added.")

    # bn
    for v in range(vec):
        for s in range(zone):
            n = v * zone + s

            col = [[[], []]]

            col[0][0].append(rowname41[n])
            col[0][1].append(-1 * cap[v])

            col[0][0].append(rowname43[n])
            col[0][1].append(1 * cap[v])

            for z in range(zone):
                col[0][0].append(rowname5[v * zone * zone + z * zone + s])
                col[0][1].append(dis[s][z])

            col[0][0].append(rowname6[v])
            col[0][1].append(1)

            prob.variables.add(
                obj=[0],
                ub=[2], lb=[0],
                types="B",
                columns=col,
                names=["bn" + str(n)]
            )

    print("bn added.")

    # # Write out optimization problem
    # prob.write("lpex-trailer.lp")

    # Initialize
    yp_total = [0.0 for s in range(zone)]
    yn_total = [0.0 for s in range(zone)]

    # Try solving optimization problem
    try:
        prob.solve()

        x = prob.solution.get_values()

        # Extract solution in terms of yp, yn, bn
        # yp, yn
        for v in range(vec):
            for s in range(zone):
                yp_total[s] += x[trainsample * zone * 2 + v * zone + s]
                yn_total[s] += x[trainsample * zone * 2 + vec * zone + v * zone + s]
        
        # bn
        bn = [[0 for s in range(zone)] for v in range(vec)]
        for v in range(vec):
            for s in range(zone):
                bn[v][s] = x[trainsample * zone * 2 + vec * zone * 3 + v * zone + s]
        
        status = 0
    
    # If no solution, no rebalancing is performed
    except CplexSolverError:

        bn = location

        status = 1

    return status, yp_total, yn_total, bn
