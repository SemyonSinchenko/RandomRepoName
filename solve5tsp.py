import sys
from pathlib import Path

import networkx as nx
import numpy as np
from qboard import Solver

from solution.converters import tsp2qubo
from solution.energy_utils import energy2time
from solution.graph_utils import csv2graph

if __name__ == "__main__":
    out_prefix = sys.argv[1]
    base_prefix = Path(out_prefix)
    base_prefix.mkdir(exist_ok=True, parents=True)

    passwd = "ebb7770c-4360-4a13-a2bc-240a8c59c51c"
    params = {
        "remote_addr": "https://remote.qboard.tech",
        "access_key": passwd
    }

    problem = csv2graph(Path(__file__).parent.joinpath("data").joinpath("paths.csv"))
    g = problem[0]
    qubo, a, n = tsp2qubo(g)
    s = Solver(mode="remote:simcim", params=params)

    spins, energy = s.solve_qubo(qubo, timeout=30)

    qboard_sol = [0,]
    for i in range(g.number_of_nodes()):
        k = 0
        for i, spin in enumerate(spins[i * g.number_of_nodes():(i+1) * g.number_of_nodes()]):
            if spin == 1:
                k = i
        qboard_sol.append(k)

    print("Solution from the QBOARD:")
    print(qboard_sol)
    print(f"Cost from QBOARD: {energy2time(energy, a, n):.2f}")
    print("Solution from nwetworkx.algorithms.approximation.traveling_salesman_problem for the same Graph")

    nx_sol = nx.algorithms.approximation.traveling_salesman_problem(g)
    print(nx_sol)
    nx_e = 0
    for i in range(len(nx_sol) - 1):
        nx_e += g.get_edge_data(nx_sol[i], nx_sol[i + 1])["weight"]
    print(f"Cost from NX: {nx_e:.2f}")

    np.savetxt(str(base_prefix.joinpath("QUBO.csv").absolute()), qubo, delimiter=",", fmt="%.4f")
    with base_prefix.joinpath("graph_path.csv").open("w") as f_:
        f_.write(",".join(map(lambda x: problem[1].get(x), qboard_sol)))