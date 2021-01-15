"""Calculate all standard electrode positions.

See README for information about assumptions.
"""
# Copyright (c) 2018-2021, Stefan Appelhoff
# BSD-3-Clause

import os

import pandas as pd
import numpy as np

from eeg_positions.contour_labels import (
    ALL_CONTOURS,
    ALL_CONTOURS2,
    SYSTEM1005,
    SYSTEM1010,
    SYSTEM1020,
)
from eeg_positions.utils import (
    find_point_at_fraction,
    get_xyz,
    plot_2d_head,
    plot_spherical_head,
    stereographic_projection,
)

if __name__ == "__main__":

    equator = "Nz-T10-Iz-T9"
    # equator = "Fpz-T8-Oz-T7"

    # Known locations
    # ---------------
    Cz = (0.0, 0.0, 1.0)
    if equator == "Nz-T10-Iz-T9":
        front = (0.0, 1.0, 0.0)
        right = (1.0, 0.0, 0.0)
        back = (0.0, -1.0, 0.0)
        left = (-1.0, 0.0, 0.0)
    elif equator == "Fpz-T8-Oz-T7":
        front = (0.0, 1.0, 0.0)
        right = (1.0, 0.0, 0.0)
        back = (0.0, -1.0, 0.0)
        left = (-1.0, 0.0, 0.0)
    else:
        raise ValueError("`equator` must be one of ['Nz-T10-Iz-T9', 'Fpz-T8-Oz-T7'].")

    d = {
        "label": equator.split("-") + ["Cz"],
        "x": [front[0], right[0], back[0], left[0], Cz[0]],
        "y": [front[1], right[1], back[1], left[1], Cz[1]],
        "z": [front[2], right[2], back[2], left[2], Cz[2]],
    }

    df = pd.DataFrame.from_dict(d)

    # Calculate all positions
    # -----------------------
    if equator == "Nz-T10-Iz-T9":
        contour_order = ALL_CONTOURS
    else:
        contour_order = ALL_CONTOURS2[:-5]
        contour_order_late = ALL_CONTOURS2[-5:]

    for contour in contour_order:

        if len(contour) == 21:
            midpoint_idx = 10
        elif len(contour) == 17:
            midpoint_idx = 8
        else:
            raise ValueError(
                "contour must be of len 17 or 21 but is {}".format(len(contour))
            )

        # Get the reference points from data frame
        p1 = get_xyz(df, contour[0])
        p2 = get_xyz(df, contour[midpoint_idx])
        p3 = get_xyz(df, contour[-1])

        # Calculate all other points at fractions of distance
        # see `contour_labels.py` and `test_contour_labels.py`
        other_ps = {}
        for i, label in enumerate(contour):
            other_ps[label] = find_point_at_fraction(
                p1, p2, p3, frac=i / (len(contour) - 1)
            )

        # Append to data frame
        tmp = pd.DataFrame.from_dict(other_ps, orient="index")
        tmp.columns = ["x", "y", "z"]
        tmp["label"] = tmp.index
        df = df.append(tmp, ignore_index=True, sort=True)

        # Remove duplicates, keeping the first computations
        df = df.drop_duplicates(subset="label", keep="first")

    if equator == "Fpz-T8-Oz-T7":
        # we need to add some more positions
        frac_modifier = 1 / len(ALL_CONTOURS2[0])
        other_ps = {}
        other_ps["OIz"] = find_point_at_fraction(
            front, Cz, back, frac=1 + (1 * frac_modifier)
        )
        other_ps["Iz"] = find_point_at_fraction(
            front, Cz, back, frac=1 + (2 * frac_modifier)
        )
        other_ps["NFpz"] = find_point_at_fraction(
            back, Cz, front, frac=1 + (1 * frac_modifier)
        )
        other_ps["Nz"] = find_point_at_fraction(
            back, Cz, front, frac=1 + (2 * frac_modifier)
        )
        other_ps["T10h"] = find_point_at_fraction(
            left, Cz, right, frac=1 + (1 * frac_modifier)
        )
        other_ps["T10"] = find_point_at_fraction(
            left, Cz, right, frac=1 + (2 * frac_modifier)
        )
        other_ps["T9h"] = find_point_at_fraction(
            right, Cz, left, frac=1 + (1 * frac_modifier)
        )
        other_ps["T9"] = find_point_at_fraction(
            right, Cz, left, frac=1 + (2 * frac_modifier)
        )

        # Append to data frame
        tmp = pd.DataFrame.from_dict(other_ps, orient="index")
        tmp.columns = ["x", "y", "z"]
        tmp["label"] = tmp.index
        df = df.append(tmp, ignore_index=True, sort=True)

        # Remove duplicates, keeping the first computations
        df = df.drop_duplicates(subset="label", keep="first")

        # draw final contours
        for contour in contour_order_late:

            if len(contour) == 21:
                midpoint_idx = 10
            elif len(contour) == 17:
                midpoint_idx = 8
            else:
                raise ValueError(
                    "contour must be of len 17 or 21 but is {}".format(len(contour))
                )

            # Get the reference points from data frame
            p1 = get_xyz(df, contour[0])
            p2 = get_xyz(df, contour[midpoint_idx])
            p3 = get_xyz(df, contour[-1])

            # Calculate all other points at fractions of distance
            # see `contour_labels.py` and `test_contour_labels.py`
            other_ps = {}
            for i, label in enumerate(contour):
                other_ps[label] = find_point_at_fraction(
                    p1, p2, p3, frac=i / (len(contour) - 1)
                )

            # Append to data frame
            tmp = pd.DataFrame.from_dict(other_ps, orient="index")
            tmp.columns = ["x", "y", "z"]
            tmp["label"] = tmp.index
            df = df.append(tmp, ignore_index=True, sort=True)

            # Remove duplicates, keeping the first computations
            df = df.drop_duplicates(subset="label", keep="first")

    # Save The positions as files for the three main standard systems
    # ---------------------------------------------------------------
    fpath = os.path.dirname(os.path.realpath(__file__))
    fname_template = os.path.join(fpath, "..", "data", "standard_{}.tsv")

    # First in 3D, then in 2D for each system
    for system, fmt in zip(
        [SYSTEM1020, SYSTEM1010, SYSTEM1005], ["1020", "1010", "1005"]
    ):

        idx = df.label.isin(system)
        system_df = df.loc[idx, :]
        system_df = system_df.sort_values(by="label")
        system_df.to_csv(
            fname_template.format(fmt),
            sep="\t",
            na_rep="n/a",
            index=False,
            float_format="%.4f",
        )

        # Now in 2D using stereographic projection
        xs, ys = stereographic_projection(
            system_df["x"].to_numpy(),
            system_df["y"].to_numpy(),
            system_df["z"].to_numpy(),
        )
        system_df = system_df.loc[:, ["label", "x", "y"]]
        system_df.loc[:, "x"] = xs
        system_df.loc[:, "y"] = ys
        system_df.to_csv(
            fname_template.format(fmt + "_2D"),
            sep="\t",
            na_rep="n/a",
            index=False,
            float_format="%.4f",
        )

    # Plot for each standard system
    # -----------------------------
    system = input("Which system do you want to plot? (1020/1010/1005/None)\n")
    if system in ["1020", "1010", "1005"]:
        df = pd.read_csv(fname_template.format(system), sep="\t")

        # 3D
        fig, ax = plot_spherical_head()

        for idx, row in df.iterrows():
            ax.scatter3D(row.x, row.y, row.z, c="b")
            ax.text(row.x, row.y, row.z, row["label"], fontsize=5)

        ax.set_title("standard_{}".format(system))

         # 2D
        df = pd.read_csv(fname_template.format(system + "_2D"), sep="\t")

        if equator == "Nz-T10-Iz-T9":
            radius_inner_contour = np.abs(df[df["label"] == "Oz"]["y"])
        else:
            radius_inner_contour = None
        fig2, ax2 = plot_2d_head(radius_inner_contour)

        ax2.scatter(df["x"], df["y"], marker=".", color="r")

        for lab, x, y in zip(list(df["label"]), df["x"], df["y"]):
            ax2.annotate(lab, xy=(x, y), fontsize=5)

        ax2.set_title("standard_{}".format(system))

        # Show and wait until done
        fig.show()
        fig2.show()
        done = input("\nClick Enter when finished viewing.\n")
