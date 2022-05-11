import os
import pandas as pd

from analysis_runs.utils import *
import rpy2
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri


dendextend = importr('dendextend')
pvclust = importr("pvclust")
grdevices = importr('grDevices')


def create_dendro_groups_file():
    file = os.path.join(PATH_STUDY, "output_data", "dendro_tanglegrams", "dendro_groups.tsv")
    if not os.path.exists(file):
        with open(file, "w") as f:
            f.write("\t".join(["group name", "column", "color", "element (B for branch, L for leave)"]))
        print(f"dendro_groups.tsv file created in path : {file}")
    else:
        print(f"dendro_groups.tsv file already exists in path : {file}")


def get_dendro_pvclust(df_binary, name, run):
    # Make pandas dataframe compatible with R dataframe.
    pandas2ri.activate()

    # Launch pvclust on the data silently and in parallel.
    result = pvclust.pvclust(df_binary, method_dist="binary", method_hclust="complete", nboot=10, quiet=True, parallel=True)

    # Create the dendrogram picture.
    out_dir = os.path.join(PATH_STUDY, f"{name}_pvclust_dend.png")
    grdevices.png(file=out_dir, width=2048, height=2048, pointsize=24)
    pvclust.plot_pvclust(result)
    grdevices.dev_off()

    # Dendextend dendrogram
    dendro_groups_file = os.path.join(PATH_STUDY, "output_data", "dendro_tanglegrams", "dendro_groups.tsv")
    create_dendextend(result, name, dendro_groups_file, run)


def get_groups(d_grp, run):
    groups_branch = {}
    groups_leaves = {}
    for i in d_grp.index:
        group = (d_grp.loc[i, "group name"], d_grp.loc[i, "column"])
        color = d_grp.loc[i, "color"]
        element = d_grp.loc[i, "element (B for branch, L for leave)"]
        group_list = get_grp_l(run, group)
        if element == "B":
            groups_branch[group] = {"list": group_list, "color": color}
        elif element == "L":
            groups_leaves[group] = {"list": group_list, "color": color}
    return groups_branch, groups_leaves


def set_branch_color(dend, groups_branch):
    for gval in groups_branch.values():
        value = rpy2.robjects.StrVector(gval["list"])
        color = rpy2.robjects.StrVector([gval["color"]])
        dend = dendextend.set(dend, "by_labels_branches_col", value=value, TF_values=color)
    return dend


def set_labels_color(dend, groups_branch):
    lab = rpy2.robjects.r['labels'](dend)
    lab_color = []
    for sp in lab:
        in_list = False
        for gval in groups_branch.values():
            if sp in gval["list"]:
                in_list = True
                lab_color.append(gval["color"])
        if not in_list:
            lab_color.append("black")
    lab_color = rpy2.robjects.StrVector(lab_color)
    dend = dendextend.set(dend, "labels_col", lab_color)
    return dend


def set_leaves_color(dend, groups_leaves):
    lab = rpy2.robjects.r['labels'](dend)
    leaves_color = []
    leaves_pch = []
    for sp in lab:
        in_list = False
        for gval in groups_leaves.values():
            if sp in gval["list"]:
                in_list = True
                leaves_color.append(gval["color"])
                leaves_pch.append(19)
        if not in_list:
            leaves_color.append("0")
            leaves_pch.append(0)
    leaves_color = rpy2.robjects.StrVector(leaves_color)
    leaves_pch = rpy2.robjects.IntVector(leaves_pch)
    dend = dendextend.set(dend, "leaves_col", leaves_color)
    dend = dendextend.set(dend, "leaves_pch", leaves_pch)
    return dend


def set_abbr_labels(dend):
    abbr_label = []
    for l in rpy2.robjects.r['labels'](dend):
        abbr_label.append(get_abbr_name(l))
    abbr_label = rpy2.robjects.StrVector(abbr_label)
    dend = dendextend.set(dend, "labels", abbr_label)
    return dend


def create_dendextend(pvclust_res, name, dendro_groups_file, run):
    d_grp = pd.read_csv(dendro_groups_file, sep="\t")

    # Get groups
    groups_branch, groups_leaves = get_groups(d_grp, run)

    # Create dendrograms
    dend = rpy2.robjects.r['as.dendrogram'](pvclust_res)
    dend = dendextend.set(dend, "branches_lwd", 4)

    # Branch Color
    dend = set_branch_color(dend, groups_branch)

    # Labels Color
    dend = set_labels_color(dend, groups_branch)

    # Leaves Color
    dend = set_leaves_color(dend, groups_leaves)

    dend = rpy2.robjects.r['sort'](dend, type="nodes")
    dend = set_abbr_labels(dend)

    # Save figure

    title = f"{name} metabolic dendrogram"
    out_dir = os.path.join(PATH_STUDY, f"{name}_dendextend_dend.png")
    grdevices.png(file=out_dir, width=2048, height=2048, pointsize=24)
    rpy2.robjects.r.plot(dend, horiz=True, main=title)
    grdevices.dev_off()


create_dendro_groups_file()
R04 = "run04"
REACTIONS = get_reactions_inst(runs=[R04])
df = REACTIONS[R04].data_reactions
get_dendro_pvclust(df, "pouet", R04)
