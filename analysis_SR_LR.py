from analysis_runs.utils import *
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

R04 = "run04"
ORG_TSV = "data/species_group.tsv"
# ### compare SR & LR #############################################################################

# compare_groups(R04, ("SR", 2), ("LR", 2), ORG_TSV)

intersect_groups(R04, ("LR", 2), ("SR", 2), ORG_TSV, True)

# Corelation nb rnx & fragmentation


def reg_lin(file_tsv):
    df = pd.read_csv(file_tsv, sep="\t", index_col="sp")
    X = list(df["#contigs"])
    Y = list(df["#rnx"])

    res = stats.linregress(x=X, y=Y)
    # reg_line = res.slope * X + res.intercept
    print(res.rvalue)

    axes = plt.axes()
    axes.grid()
    plt.scatter(X, Y)
    # plt.plot(X, reg_line, c='r')
    plt.xlabel("#contigs")
    plt.ylabel("#rnx")
    plt.show()
