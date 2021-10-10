import csv
# import time

from get_data_common import main as get_data_common
from get_data_case import main as get_data_case
from initialize_location import initialize_location
from update_ds import main as update_ds
from initialize_cluster import initialize_cluster
from modify_cluster.modify_cluster import modify_cluster
from intra_redeployment import main as intra_redeployment

# Settings
htime = 13  # number of planning periods/timesteps
zone = 241  # station number

# Parameters
trainsample = 10
vec = 50  # operator number
cap = [3 for i in range(50)]  # operator capacity
dismaxpick = 50  # maximum distance to pick-up
dismaxdrop = 50  # maximum dsitance from pick-up to drop-off
cluster = 15  # cluster number

# Read common data
cp, dis, mindis, fl = get_data_common(htime, zone, trainsample)


def main(input_scenario):
    """
    Generate and write bike rebalancing policy for input scenario.

    Paramters
    ----------
    input_scenario: int
        index of input scenario
    """

    print("Program running for demand scenario " + str(input_scenario))

    policy_f = open("./Policy/policy_result" + str(input_scenario) + ".csv", "w", newline='')
    policy_writer = csv.writer(policy_f)

    # Read case data
    ds, orig_fl = get_data_case(input_scenario, htime, zone)

    # Initialize operator location
    location = initialize_location(zone, vec)

    # Initialize cluster
    assignment, centre = initialize_cluster(cluster, zone, mindis)

    # Run
    # Timestep 0
    ds = update_ds(zone, cp, ds, mindis, orig_fl[0])

    # Timestep 1:
    for timestep in range(1, htime):

        print("Running for timestep " + str(timestep))

        # Extract demand flows in current timestep
        train_fl = [fl[ts][timestep] for ts in range(trainsample)]

        # Compute total demand flows in and out of each station
        train_fl_out = [[0 for s in range(zone)] for ts in range(trainsample)]
        train_fl_in = [[0 for s in range(zone)] for ts in range(trainsample)]

        for ts in range(trainsample):
            for s in range(zone):
                train_fl_out[ts][s] = sum(train_fl[ts][s])
                for z in range(zone):
                    train_fl_in[ts][s] += train_fl[ts][z][s]

        # Modify cluster based on demand flows
        assignment = modify_cluster(cluster, assignment, centre, zone, cp, ds, mindis, trainsample, train_fl)
        print("Clusters generated.")

        # Initialize global intra-cluster rebalancing result
        yp_total = [0.0 for s in range(zone)]
        yn_total = [0.0 for s in range(zone)]
        bn = [[0 for s in range(zone)] for v in range(vec)]

        # Intra-cluster rebalancing
        for c in range(cluster):

            # Extract local data
            local_list = [s for s in range(zone) if assignment[s] == c]

            local_zone = len(local_list)

            local_cp = [cp[s] for s in local_list]
            local_ds = [ds[s] for s in local_list]

            local_vec_list = []
            local_vec = 0
            local_cap = []
            local_location = []

            for v in range(vec):
                if location[v].index(1) in local_list:
                    local_vec_list.append(v)
                    local_vec += 1
                    local_cap.append(cap[v])
                    local_location.append([1 if (s == location[v].index(1)) else 0 for s in local_list])
            
            local_dis = [[dis[s][z] for z in local_list] for s in local_list]

            local_train_fl_out = [[train_fl_out[ts][s] for s in local_list] for ts in range(trainsample)]
            local_train_fl_in = [[train_fl_in[ts][s] for s in local_list] for ts in range(trainsample)]

            # Apply local rebalance
            status, local_yp_total, local_yn_total, local_bn = intra_redeployment(local_zone, local_cp, local_ds, local_vec, local_cap, local_location, local_dis, trainsample, local_train_fl_out, local_train_fl_in, dismaxpick, dismaxdrop)

            # Make error report if no solution
            if status == 1:
                error_f = open("./error_report.csv", "a", newline='')
                error_writer = csv.writer(error_f)
                error_writer.writerow([str(cluster), str(input_scenario), str(timestep), str(c)])
                error_f.close()

            # Translate to global indexing
            for s in range(local_zone):
                yp_total[local_list[s]] = local_yp_total[s]
                yn_total[local_list[s]] = local_yn_total[s]
            
            for v in range(local_vec):
                for s in range(local_zone):
                    bn[local_vec_list[v]][local_list[s]] = local_bn[v][s]
        
            print("Cluster done is: " + str(c))
        
        for s in range(zone):
            policy_writer.writerow([str(timestep), str(s), str(yp_total[s]), str(yn_total[s])])
        
        # Update ds
        update_ds(zone, cp, ds, mindis, orig_fl[timestep], yp_total, yn_total)

        # Update operator location
        for v in range(vec):
            for s in range(zone):
                if round(bn[v][s]) == 1:
                    location[v][s] = 1
                else:
                    location[v][s] = 0
        
        print("Timestep done is: " + str(timestep))
    
    policy_f.close()
