"""Calculate standard EEG electrode positions on a sphere."""
# Copyright (c) 2018-2021, Stefan Appelhoff
# BSD-3-Clause

import os
from distutils.version import LooseVersion

import numpy as np
import pandas as pd

from eeg_positions.config import (
    ACCEPTED_EQUATORS,
    MNE_REQUIREMENT,
    RADIUS_INNER_CONTOUR,
    SYSTEM1005,
    SYSTEM1010,
    SYSTEM1020,
    CONTOUR_ORDER_Fpz_EQUATOR,
    CONTOUR_ORDER_Nz_EQUATOR,
)
from eeg_positions.utils import (
    _add_points_along_contour,
    _append_ps_to_df,
    _stereographic_projection,
    find_point_at_fraction,
)
from eeg_positions.viz import _plot_2d_head, _plot_spherical_head


def get_alias_mapping():
    """Get a mapping from electrode names to their aliases.

    Some electrode positions have multiple names (aliases), depending
    on the convention that was used to name them.
    With this function, electrodes that are typically not part of the
    10-20, 10-10, or 10-05 namespace are mapped to their alias within
    these systems.

    Returns
    -------
    alias_mapping : dict
        A dictionary mapping electrode names to a list of alias
        names.

    Notes
    -----
    Some electrodes do not have a direct alias but an approximately
    corresponding position. For example "A1" corresponds to the
    "LPA" position with some (x, y, z) offset in the coordinate
    system. These positions are returned with a mapping like:
    ``{"name": "alias+(x, y, z)"}``.

    Examples
    --------
    >>> alias_mapping = get_alias_mapping()
    >>> alias_mapping["T3"]
    'T7'
    >>> alias_mapping["A1"]
    'LPA+(0.1, 0.1, 0.1)'

    """
    # TODO: add aliases, correct A1 alias
    alias_mapping = dict(
        T3="T7",
        A1="LPA+(0.1, 0.1, 0.1)",
    )
    return alias_mapping


def get_available_elec_names(system="all"):
    """Get a list of electrode names for which positions are available.

    Parameters
    ----------
    system : "1020" | "1010" | "1005" | "all"
        Specify for which system to return the electrode names.
        If ``"all"``, return all electrode names for which positions
        are available. Defaults to ``"all"``.

    Returns
    -------
    elec_names : list of str
        The electrode names for which positions are available.

    See Also
    --------
    get_alias_mapping
    get_elec_coords

    Examples
    --------
    >>> elec_names = get_available_elec_names()
    >>> "FakeName" in elec_names
    False
    >>> "Cz" in elec_names
    True

    """
    elec_names = {
        "1020": SYSTEM1020,
        "1010": SYSTEM1010,
        "1005": SYSTEM1005,
        "all": (SYSTEM1005 + list(get_alias_mapping().keys())),
    }
    elec_names = elec_names.get(system, None)
    if elec_names is None:
        raise ValueError(f"Unknown input for `system`: {system}")
    return elec_names


def get_elec_coords(
    system="1005",
    elec_names=None,
    drop_landmarks=False,
    dim="2d",
    as_mne_montage=False,
    equator="Nz-T10-Iz-T9",
):
    """Get standard EEG electrode coordinates.

    Compute standard EEG electrode coordinates on a spherical head model.

    Parameters
    ----------
    system : "1020" | "1010" | "1005"
        Specify the electrodes for which to return coordinates.
        ``"1020"`` returns all electrodes of the 10-20 system, and so on.
        For an overview of the systems, see [1]_.
        Defaults to ``"1005"``.
        A more specific selection of electrodes to return can be done with
        the `elec_names` parameter, including some electrodes that are not
        typically included in the ``"1005"`` system.
        If `elec_names` is defined, `system` is ignored.
    elec_names : list of str | None
        List of electrode names to return coordinates of.
        All electrodes that are part of the ``"1005"`` system are available,
        and this includes by definition all electrodes of the
        ``"1010"`` and ``"1020"`` systems.
        Additionally, several extra electrodes are made available.
        Use :func:`get_available_elec_names` and
        :func:`get_alias_mapping` for more information.
        If ``None``, all electrode specified in `system` are returned.
        Defaults to ``None``.
    drop_landmarks : bool
        If True, drop anatomical landmarks (NAS, LPA, RPA)
        from the coordinate data before returning `coords`. Dropping is helpful,
        because in our model NAS, LPA, and RPA coincide with Nz, T9, and T10
        respectively.
        Defaults to ``True``.
    dim : "2d" | "3d"
        Return `coords` either in 2D (x, y) or 3D (x, y, z). If ``"2d"`` is
        selected, the coordinates are first computed as 3D, and then projected
        to 2D using a stereographic projection.
        Defaults to ``"2d"``.
    as_mne_montage : bool
        If True, return `coords` as an ``mne.channels.DigMontage`` object. In that
        case, the `drop_landmarks` and `dim` parameters are set to ``False`` and
        ``"3d"`` respectively, ignoring the values that were actually passed.
        This is done because the anatomical landmarks are needed to "fit" the
        coordinates to the mne system, and because ``mne.channels.DigMontage``objects
        always contain 3D values. If ``True``, a recent version of ``mne`` is required.
        Defaults to ``False``, returning `coords` as a ``pandas.DataFrame`` object.
    equator_contour : "Nz-T10-Iz-T9" | "Fpz-T8-Oz-T7"
        Control which contour line of electrodes should be at the equator of
        the sphere. Both permissible options (``"Nz-T10-Iz-T9"`` or ``"Fpz-T8-Oz-T7"``)
        are reasonable assumptions.
        Selecting ``"Nz-T10-Iz-T9"`` is recommended, because the electrodes Nz, T9,
        and T10 correspond to the anatomical landmarks NAS, LPA, and RPA in
        our spherical head model (see Notes section).
        Thus, the anatomical landmarks lie on the equator,
        and all electrodes are drawn inside a circule head shape
        when projecting to 2D.
        The option to select ``"Fpz-T8-Oz-T7"`` is provided (but not recommended),
        because this contour line corresponds to where the head circumference
        would be measured for real humans. However, when selecting ``"Fpz-T8-Oz-T7"``
        as the equator, several electrodes may be drawn outside a circular
        head shape when projecting to 2D.
        Defaults to ``"Nz-T10-Iz-T9"``.

    Returns
    -------
    coords : pandas.DataFrame | mne.channels.DigMontage
        The standard EEG electrode coordinates as computed on a sphere.
        Either returned as a pandas DataFrame object with the columns
        ``"label"``, ``"x"``, ``"y"``, and ``"z"``
        (only if `dim` is ``"3d"``),
        or as an ``mne.channels.DigMontage`` object if `as_mne_montage`
        is ``True``.

    See Also
    --------
    get_available_elec_names
    get_alias_mapping

    Notes
    -----
    We are modelling the coordinate system as if a subject's head was
    a sphere.
    Coordinates are computes according to a "RAS" coordinate system
    (Right, Anterior, Superior). That is, from a subject's perspective
    the x-axis points from the left to the right,
    the y-axis points to the front (anterior direction), and
    the z-axis points up (superior direction).
    For example a point on the subject's left side will have a
    negative ``x`` coordinate value.

    The location of the origin of the sphere depends on the argument to
    the `equator` parameter.

    In the recommended case ``"Nz-T10-Iz-T9"``,
    the coordinate system is based on anatomical landmarks:
    The left preauricular point (LPA), the right preauricular
    point (RPA), and the nasion (NAS).
    The x-axis goes from LPA through RPA, the y-axis goes orthogonally
    to the x-axis through NAS, and the z-axis goes orthogonally
    upwards from the xy-plane, going directly through the vertex
    of the sphere, coinciding with the ``"Cz"`` electrode position.
    In that case, the origin of the sphere lies somewhere between the ears,
    but not necessarily exactly in the middle.

    If the option is selected to put the equator on the ``"Fpz-T8-Oz-T7"``
    contour, the anatomical landmarks end up *below* the equator, and
    the origin of the sphere lies somewhere between the ``"T7"`` and ``"T8"``
    electrode positions.

    The units of the coordinate system are arbitrary, because all coordinates
    are computed on a unit sphere (that is, a sphere with radius 1).

    References
    ----------
    .. [1] R. Oostenveld and P. Praamstra. The five percent electrode system for
       high-resolution EEG and ERP measurements. Clin Neurophysiol, 112:713-719, 2001.
       https://doi.org/10.1016/S1388-2457(00)00527-7

    """
    # Perform input checks
    # --------------------
    if equator not in ACCEPTED_EQUATORS:
        raise ValueError(f"`equator` must be one of {ACCEPTED_EQUATORS}.")

    systems = {"1020": SYSTEM1020, "1010": SYSTEM1010, "1005": SYSTEM1005}
    system = systems.get(system, None)
    if system is None:
        raise ValueError(f"`system` must be one of {list(systems.keys())}.")

    if elec_names is None:
        elec_names = []
    if not isinstance(elec_names, (list, type(None))):
        raise ValueError("`elec_names` must be a list of str or None.")

    available_elec_names = get_available_elec_names()
    bad_elec_names = set(elec_names) - set(available_elec_names)
    if len(bad_elec_names) > 0:
        msg = (
            f"For some `elec_names` there are no available positions: {bad_elec_names}"
            f"\nDid you check for proper capitalization?"
            f"\nSee also the `get_available_elec_names` function."
        )
        raise ValueError(msg)

    dims = ["2d", "3d"]
    if dim not in dims:
        raise ValueError(f"`dim` must be one of {dims}.")

    for val, name in zip(
        (as_mne_montage, drop_landmarks), ("as_mne_montage", "drop_landmarks")
    ):
        if not isinstance(val, bool):
            raise ValueError(f"`{name}` must be a boolean value, but found: {val}")

    # Calculate positions
    # -------------------
    # Known locations
    front = (0.0, 1.0, 0.0)
    right = (1.0, 0.0, 0.0)
    back = (0.0, -1.0, 0.0)
    left = (-1.0, 0.0, 0.0)
    top = (0.0, 0.0, 1.0)

    d = {
        "label": equator.split("-") + ["Cz"],
        "x": [front[0], right[0], back[0], left[0], top[0]],
        "y": [front[1], right[1], back[1], left[1], top[1]],
        "z": [front[2], right[2], back[2], left[2], top[2]],
    }

    df = pd.DataFrame.from_dict(d)

    # Check the order of contours to draw based on known locations
    if equator == "Nz-T10-Iz-T9":
        contour_order = CONTOUR_ORDER_Nz_EQUATOR
    else:
        assert equator == "Fpz-T8-Oz-T7"
        contour_order = CONTOUR_ORDER_Fpz_EQUATOR[:-5]
        contour_order_late = CONTOUR_ORDER_Fpz_EQUATOR[-5:]

    # draw everything that we can draw
    for contour in contour_order:
        df = _add_points_along_contour(df, contour)

    # for the Fpz equator, we need to compute some points "manually"
    # before drawing final contours
    if equator == "Fpz-T8-Oz-T7":
        frac_modifier = 1 / len(CONTOUR_ORDER_Fpz_EQUATOR[0])
        other_ps = {}
        p_to_find = ["OIz", "Iz", "NFpz", "Nz", "T10h", "T10", "T9h", "T9"]
        p_fracs = [1, 2, 1, 2, 1, 2, 1, 2]
        p_arc = (
            [(front, top, back)] * 2
            + [(back, top, front)] * 2
            + [(left, top, right)] * 2
            + [(right, top, left)][::-1] * 2
        )

        for label, frac, arc in zip(p_to_find, p_fracs, p_arc):
            other_ps[label] = find_point_at_fraction(
                *arc, frac=1 + (frac * frac_modifier)
            )

        # Append to data frame
        df = _append_ps_to_df(df, other_ps)

        # draw final contours for Fpz equator
        for contour in contour_order_late:
            df = _add_points_along_contour(df, contour)

    # subselect electrodes
    # --------------------
    if len(elec_names) > 0:
        selection = df.label.isin(elec_names)
    else:
        selection = df.label.isin(system)
    df_selection = df.loc[selection, :]

    # Return as mne DigMontage object (or not)
    # ----------------------------------------
    if as_mne_montage:
        # Check that we have an appropriate version
        try:
            __import__("mne")
        except ImportError:
            raise ImportError(
                "if `as_mne_montage` is True, you must have mne installed."
            )
        else:
            import mne

            mne_version = mne.__version__
            msg = (
                f"You need to update your mne installation. Version {MNE_REQUIREMENT} "
                f"or higher is required, but you have {mne_version}."
            )
            if LooseVersion(mne_version) < LooseVersion(MNE_REQUIREMENT):
                raise RuntimeError(msg)

        # Now convert to DigMontage (first using the full df once more)
        # NOTE: set to MNE default head size radius (in meters)
        ch_pos = df.set_index("label").to_dict("index")
        for key, val in ch_pos.items():
            ch_pos[key] = (
                np.asarray(list(val.values())) * mne.defaults.HEAD_SIZE_DEFAULT
            )

        NAS = ch_pos["Nz"]
        LPA = ch_pos["T9"]
        RPA = ch_pos["T10"]

        # Make the sub-selection of channels again
        selection = elec_names if len(elec_names) > 0 else system
        ch_pos = {key: val for key, val in ch_pos.items() if key in selection}

        coords = mne.channels.make_dig_montage(
            ch_pos=ch_pos, nasion=NAS, lpa=LPA, rpa=RPA
        )

        # return early, ignoring landmarks and 2D projection
        return coords

    # Else, if no mne DigMontage is wanted:
    # add landmarks (or not)
    # ----------------------
    # Nz = NAS, T9 = LPA, T10 = RPA
    if not drop_landmarks:
        tmp = df.loc[df["label"].isin(["Nz", "T9", "T10"]), ["x", "y", "z"]]
        tmp.insert(0, "label", ["NAS", "LPA", "RPA"])
        df_selection = df_selection.append(tmp, ignore_index=True, sort=True)

    # Project to 2d (or not)
    # ----------------------
    if dim == "2d":
        xs, ys = _stereographic_projection(
            df_selection["x"].to_numpy(),
            df_selection["y"].to_numpy(),
            df_selection["z"].to_numpy(),
        )
        df_selection = df_selection.loc[:, ["label", "x", "y"]]
        df_selection.loc[:, "x"] = xs
        df_selection.loc[:, "y"] = ys

    coords = df_selection.sort_values(by="label")
    return coords


if __name__ == "__main__":

    # Save The positions as files for the three main standard systems
    # ---------------------------------------------------------------
    fpath = os.path.dirname(os.path.realpath(__file__))
    fname_template = os.path.join(fpath, "..", "data", "standard_{}_{}.tsv")

    # First in 3D, then in 2D for each system
    for system in ["1020", "1010", "1005"]:
        for dim in ["2D", "3D"]:
            coords = get_elec_coords(
                system=system,
                elec_names=None,
                drop_landmarks=True,
                dim=dim.lower(),
                as_mne_montage=False,
                equator="Nz-T10-Iz-T9",
            )

            coords.to_csv(
                fname_template.format(system, dim),
                sep="\t",
                na_rep="n/a",
                index=False,
                float_format="%.4f",
            )

    # Plot for each standard system
    # -----------------------------
    fname_template = "./data/standard_{}_{}.tsv"
    system = input("Which system do you want to plot? (1020/1010/1005/None)\n")
    if system in ["1020", "1010", "1005"]:
        df = pd.read_csv(fname_template.format(system, "3D"), sep="\t")

        # 3D
        fig, ax = _plot_spherical_head()

        for idx, row in df.iterrows():
            ax.scatter3D(row["x"], row["y"], row["z"], c="b")
            ax.text(row["x"], row["y"], row["z"], row["label"], fontsize=5)

        ax.set_title(f"standard_{system}")

        # 2D
        df = pd.read_csv(fname_template.format(system, "2D"), sep="\t")

        fig2, ax2 = _plot_2d_head(RADIUS_INNER_CONTOUR)

        for idx, row in df.iterrows():
            ax2.scatter(row["x"], row["y"], marker=".", color="r")
            ax2.annotate(row["label"], xy=(row["x"], row["y"]), fontsize=5)

        ax2.set_title(f"standard_{system}")

        # Show and wait until done
        fig.show()
        fig2.show()
        input("\nClick Enter when finished viewing.\n")
