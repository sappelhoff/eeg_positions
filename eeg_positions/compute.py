"""Calculate standard EEG electrode positions on a sphere."""

import ast
import os

import numpy as np
import pandas as pd
from packaging.version import Version

from eeg_positions.config import (
    ACCEPTED_EQUATORS,
    LANDMARKS,
    MNE_REQUIREMENT,
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
        names. The keys are electrode names that are *not* in the
        10-05 namespace, but they map to values that *are* in that
        namespace. However, see also "Notes" below.

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
    >>> alias_mapping["M1"]
    'TP9'
    >>> alias_mapping["A1"]
    'LPA+(-0.1, -0.01, -0.01)'

    """
    alias_mapping = dict(
        A1="LPA+(-0.1, -0.01, -0.01)",
        A2="RPA+(0.1, -0.01, -0.01)",
        M1="TP9",
        M2="TP10",
    )

    # sanity checks
    for key, val in alias_mapping.items():
        # a value must not be a key
        assert val not in alias_mapping

        # a key must not be in the 10-05 namespace + landmarks
        assert key not in (SYSTEM1005 + LANDMARKS)

        # a key must not contain certain characters
        # so that the names do not collide with the alias+(x, y, z) syntax
        for char in "+":
            assert char not in key

        # a value must be in the 10-05 namespace + landmarks
        # or be based on such a position, if it is modified via "+(...)"
        if "+(" in val:
            # this will raise a ValueError if more than one "+" is in the str,
            # ... so do not define the tuple as something like (+1, -1, +0.3)
            name, mod = val.split("+")
            # the modifier must be a tuple of 3 ints/floats
            mod = ast.literal_eval(mod)
            isinstance(mod, tuple)
            len(mod) == 3
            isinstance(mod[0], (int, float))
            isinstance(mod[1], (int, float))
            isinstance(mod[2], (int, float))
        else:
            name = val
        assert name in (SYSTEM1005 + LANDMARKS)

    return alias_mapping


def get_available_elec_names(system="all"):
    """Get a list of electrode names for which positions are available.

    Parameters
    ----------
    system : "1020" | "1010" | "1005" | "landmarks" | "all"
        Specify for which system to return the electrode names.
        If ``"landmarks"``, return the anatomical landmark names.
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
    >>> elec_names = get_available_elec_names(system="landmarks")
    >>> print(elec_names)
    ['LPA', 'RPA', 'NAS']

    """
    elec_names = {
        "1020": SYSTEM1020,
        "1010": SYSTEM1010,
        "1005": SYSTEM1005,
        "landmarks": LANDMARKS,
        "all": (SYSTEM1005 + LANDMARKS + list(get_alias_mapping().keys())),
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
    sort=False,
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
        from the coordinate data before returning `coords`. Dropping can be helpful,
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
    sort : bool
        Whether to sort the returned coordinates alphabetically. If ``False`` (default),
        preserve the order of ``elec_names`` if available.

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
    # perform input checks
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

    # handle aliases
    # --------------
    # get dict of aliases
    alias_mapping = get_alias_mapping()

    # aliases that are in "alias+(x, y, z)" syntax are handled last (special treatment)
    elec_names_special = []

    # for position computation we rename all electrodes to the 10-05 namespace,
    # then before returning, we use the `elec_names_replaced` dict to map the
    # names back to what the users wants
    elec_names_replaced = {}
    elec_names_replaced_special = {}
    for name in elec_names:

        # skip all elec_names that are not aliases: These are fine as they are
        if name not in alias_mapping:
            continue

        # check that one position is not specified twice
        alias = alias_mapping[name]
        if alias in elec_names:
            msg = (
                f"You specified the same electrode position using two aliases: "
                f"{name}, {alias}. Remove one of them from `elec_names`."
            )
            raise ValueError(msg)

        # replace the elec_name with its alias
        if "+(" not in alias:
            # for simple cases we know that an alias is in the 10-05 namespace
            elec_names[elec_names.index(name)] = alias
            elec_names_replaced[alias] = name
        else:
            # however, some cases are specified using an "alias+(x, y, z)" format
            # we compute these electrode as the last positions (special treatment)
            assert "+(" in alias
            elec_names_special.append(alias)
            alias_name, _ = alias.split("+")
            elec_names_replaced_special[alias_name] = name

    # calculate positions
    # -------------------
    # known locations
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

    # check the order of contours to draw based on known locations
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

        # append to data frame
        df = _append_ps_to_df(df, other_ps)

        # draw final contours for Fpz equator
        for contour in contour_order_late:
            df = _add_points_along_contour(df, contour)

    # get landmark coordinates
    # ------------------------
    # based on our assumptions: Nz=NAS, T9=LPA, T10=RPA
    tmp = df.loc[df["label"].isin(["Nz", "T9", "T10"]), :].copy()
    tmp.loc[:, "label"] = tmp["label"].replace(
        to_replace=dict(Nz="NAS", T9="LPA", T10="RPA")
    )
    df = pd.concat([df, tmp], ignore_index=True)

    # if we need to return an mne montage, we need the actual coordinates
    # as ndarrays
    if as_mne_montage:
        # based on our assumptions: Nz=NAS, T9=LPA, T10=RPA
        landmark_pos = df.set_index("label").to_dict("index")
        for label in ["NAS", "LPA", "RPA"]:
            landmark_pos[label] = np.asarray(list(landmark_pos[label].values()))

    # subselect electrodes
    # --------------------
    if len(elec_names) > 0:
        selection = df.label.isin(elec_names)
        df_selection = df.loc[selection, :].copy()
        if not sort:
            df_selection = (
                df_selection.set_index("label").reindex(elec_names).reset_index()
            )
    else:
        selection = df.label.isin(system + LANDMARKS)
        df_selection = df.loc[selection, :].copy()

    # add special elec positions
    pos_to_add = {}
    for elec in elec_names_special:
        name, modifier_str = elec.split("+")
        modifier = np.array(ast.literal_eval(modifier_str))
        original = df.loc[df["label"] == name, ["x", "y", "z"]].to_numpy()
        x, y, z = np.squeeze(original + modifier)

        for col, val in zip(["label", "x", "y", "z"], [name, x, y, z]):
            pos_to_add[col] = pos_to_add.get(col, []) + [val]

    # re-name aliases of special elec positions, then add
    pos_to_add_df = pd.DataFrame.from_dict(pos_to_add)
    if len(pos_to_add_df) > 0:
        pos_to_add_df.loc[:, "label"] = pos_to_add_df["label"].replace(
            to_replace=elec_names_replaced_special
        )
        df_selection = pd.concat([df_selection, pos_to_add_df], ignore_index=True)

    # re-rename remaining aliases
    df_selection.loc[:, "label"] = df_selection["label"].replace(
        to_replace=elec_names_replaced
    )

    # return as mne DigMontage object (or not)
    # ----------------------------------------
    if as_mne_montage:
        # check that we have an appropriate version
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
            if Version(mne_version) < Version(MNE_REQUIREMENT):
                raise RuntimeError(msg)

        # now convert to DigMontage
        # NOTE: set to MNE default head size radius (in meters)
        # drop potential duplicates first
        df_selection = df_selection.drop_duplicates(subset=["label"])
        ch_pos_from_df = df_selection.set_index("label").to_dict("index")
        ch_pos = {}
        for key, val in ch_pos_from_df.items():
            if key in ["NAS", "LPA", "RPA"]:
                # landmarks are not electrode positions
                continue

            ch_pos[key] = (
                np.asarray(list(val.values())) * mne.defaults.HEAD_SIZE_DEFAULT
            )

        NAS = landmark_pos["NAS"] * mne.defaults.HEAD_SIZE_DEFAULT
        LPA = landmark_pos["LPA"] * mne.defaults.HEAD_SIZE_DEFAULT
        RPA = landmark_pos["RPA"] * mne.defaults.HEAD_SIZE_DEFAULT

        coords = mne.channels.make_dig_montage(
            ch_pos=ch_pos, nasion=NAS, lpa=LPA, rpa=RPA
        )

        # return early
        return coords

    # drop landmarks (or not)
    # -----------------------
    if drop_landmarks:
        df_selection = df_selection[~df_selection["label"].isin(["NAS", "LPA", "RPA"])]

    # project to 2d (or not)
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

    df_selection = df_selection.drop_duplicates(subset=["label"])
    if sort:
        df_selection = df_selection.sort_values(by="label")
    coords = df_selection.reset_index(drop=True)
    return coords


def _produce_files_and_do_x(x="save"):
    """Produce electrode positions and save them.

    Parameters
    ----------
    x : str
        What to do after producing each file. Can be "save", or "compare" to
        compare the produced file to a previously saved file.

    Notes
    -----
    use as follows from the command line:

    python -c "from eeg_positions.compute import _produce_files_and_do_x;\
        _produce_files_and_do_x()"

    """
    # which decimal precision to use for saving the data
    precision = 4

    fpath = os.path.dirname(os.path.realpath(__file__))
    fname_template = os.path.join(fpath, "..", "data", "{}", "standard_{}_{}.tsv")

    # For each equator for each system for both 2D and 3D
    for equator in ACCEPTED_EQUATORS:
        for system in ["1020", "1010", "1005"]:
            for dim in ["2D", "3D"]:
                coords = get_elec_coords(
                    system=system,
                    elec_names=None,
                    drop_landmarks=False,
                    dim=dim.lower(),
                    as_mne_montage=False,
                    equator=equator,
                    sort=True,
                )

                fname = fname_template.format(equator, system, dim)

                if x == "save":
                    os.makedirs(os.path.split(fname)[0], exist_ok=True)
                    coords.to_csv(
                        fname,
                        sep="\t",
                        na_rep="n/a",
                        index=False,
                        float_format=f"%.{precision}f",
                    )
                else:
                    assert x == "compare"
                    coords_read = pd.read_csv(fname, sep="\t")
                    cols = ["x", "y"] if dim == "2D" else ["x", "y", "z"]
                    data_read = coords_read[cols]
                    data_produced = coords[cols].round(precision)

                    np.testing.assert_allclose(data_read, data_produced)
