"""Functions to calculate and plot standard EEG electrode position systems."""
# Copyright (c) 2018-2021, Stefan Appelhoff
# BSD-3-Clause

import numpy as np
import pandas as pd


def find_point_at_fraction(p1, p2, p3, frac):
    """Find a point on an arc spanned by three points.

    Given three points `p1`, `p2` and `p3` on a sphere with origin (0, 0, 0),
    find the coordinates of a `point` at a fraction `frac` of the overall
    distance on an arc spanning from `p1` over `p2` to `p3`. Given this
    assumption, for fractions of zero, `point` will equal `p1`; for fractions
    of one, `point` will equal `p3`; and for fractions of one half, `point`
    will equal `p2` [1]_.

    Parameters
    ----------
    p1, p2, p3 : tuple
        Each tuple containing x, y, z cartesian coordinates.
    frac : float
        Fraction of distance from `p1` to `p3` over p2` at which
        to find coordinates of `point`.

    Returns
    -------
    point : tuple
        The x, y, z cartesian coordinates of the point at fraction.

    Notes
    -----
    The assumptions of this function require `p1`, `p2` and `p3` to be
    equidistant from the origin. They must not be collinear (i.e., all be
    along one line) and none of the points may be equal.

    References
    ----------
    .. [1] Nominal Animal
       (https://math.stackexchange.com/users/318422/nominal-animal),
       find intermediate points on small circle of a sphere,
       URL (version: 2018-06-02): https://math.stackexchange.com/q/2805204

    Examples
    --------
    >>> p1 = (1., 0., 0.)
    >>> p2 = (0., 0., 1.)
    >>> p3 = (-1., 0., 0.)
    >>> find_point_at_fraction(p1, p2, p3, frac=0.)
    (1.0, 0.0, 0.0)
    >>> find_point_at_fraction(p1, p2, p3, frac=.5)
    (0.0, 0.0, 1.0)
    >>> find_point_at_fraction(p1, p2, p3, frac=1.)
    (-1.0, 0.0, 0.0)
    >>> find_point_at_fraction(p1, p2, p3, frac=.3)
    (0.5878, 0.0, 0.809)

    """
    # Unpack the point tuples
    x1, y1, z1 = p1
    x2, y2, z2 = p2
    x3, y3, z3 = p3

    # Using the cross product, find unit normal vector (xn, yn, zn)
    # of the plane spanning the three points:
    x12 = x2 - x1
    y12 = y2 - y1
    z12 = z2 - z1
    x13 = x3 - x1
    y13 = y3 - y1
    z13 = z3 - z1

    xn = y12 * z13 - z12 * y13
    yn = z12 * x13 - x12 * z13
    zn = x12 * y13 - y12 * x13

    n = np.sqrt(xn ** 2 + yn ** 2 + zn ** 2)

    if n <= 0.0:
        raise ValueError("Points are either collinear or share the same coordinates.")

    xn = xn / n
    yn = yn / n
    zn = zn / n

    # Use dot product to get signed distance from plane to origin
    # interchangeably use p1, p2, or p3 with normal vector
    d = xn * x1 + yn * y1 + zn * z1

    # At intersection of sphere and plane, we have a circle
    # with the following center:
    xc = d * xn
    yc = d * yn
    zc = d * zn

    # Construct a 2D coordinate system with the unit circle corresponding
    # to the above circle with first axis towards p1 and second towards p2:
    # 2D U axis unit vector
    xu = x1 - xc
    yu = y1 - yc
    zu = z1 - zc

    # 2D V axis unit vector
    xv = yn * zu - zn * yu
    yv = zn * xu - xn * zu
    zv = xn * yu - yn * xu

    # Choose V axis towards (x2, y2, z2)
    v2 = (x2 - xc) * xv + (y2 - yc) * yv + (z2 - zc) * zv
    if v2 < 0.0:
        xv = -xv
        yv = -yv
        zv = -zv

    # Find theta, the positive plane angle towards p3 (x3, y3, z3).
    xt = x3 - xc
    yt = y3 - yc
    zt = z3 - zc

    thetau = xt * xu + yt * yu + zt * zu
    thetav = xt * xv + yt * yv + zt * zv
    theta = np.arctan2(thetav, thetau)

    if theta < 0.0:
        # Add 360 degrees, or 2*Pi in radians, to make it positive
        theta = theta + 2 * np.pi

    # Now calculate coordinates at fraction
    x = xc + xu * np.cos(frac * theta) + xv * np.sin(frac * theta)
    y = yc + yu * np.cos(frac * theta) + yv * np.sin(frac * theta)
    z = zc + zu * np.cos(frac * theta) + zv * np.sin(frac * theta)

    # Round to 4 decimals and collect the points in tuple
    point = np.asarray((x, y, z))
    point = tuple(point.round(decimals=4))
    return point


def _add_points_along_contour(df, contour):
    """Compute points along `contour` and add them to `df`.

    Parameters
    ----------
    df : pandas.DataFrame
        The data with columns ["label", "x", "y", "z"].
    contour : list of str
        Each entry in `contour` is the label of a point, and
        all points in `contour` are ordered. Must be of length
        17 or 21.

    Returns
    -------
    df : pandas.DataFrame
        The data with columns ["label", "x", "y", "z"] and
        new points (rows in `df`) along `contour` added.

    """
    contour_len = len(contour)
    if contour_len == 21:
        midpoint_idx = 10
    elif contour_len == 17:
        midpoint_idx = 8
    else:
        raise ValueError(f"contour must be of len 17 or 21 but is {contour_len}")

    # Get the reference points from data frame
    p1 = _get_xyz(df, contour[0])
    p2 = _get_xyz(df, contour[midpoint_idx])
    p3 = _get_xyz(df, contour[-1])

    # Calculate all other points at fractions of distance
    other_ps = {}
    for i, label in enumerate(contour):
        other_ps[label] = find_point_at_fraction(
            p1, p2, p3, frac=i / (len(contour) - 1)
        )

    # Append to data frame
    df = _append_ps_to_df(df, other_ps)
    return df


def _append_ps_to_df(df, ps):
    """Add points `ps` to data frame `df`.

    This function removes duplicates from `df`, always keeping
    the first entry it finds.

    Parameters
    ----------
    df : pandas.DataFrame
        The data with columns ["label", "x", "y", "z"].
    ps : dict
        Each key is a label, with a tuple value of (x, y, z)
        coordinates.

    Returns
    -------
    df : pandas.DataFrame
        The data with columns ["label", "x", "y", "z"],
        and `ps` added.

    """
    tmp = pd.DataFrame.from_dict(ps, orient="index")
    tmp.columns = ["x", "y", "z"]
    tmp["label"] = tmp.index
    df = df.append(tmp, ignore_index=True, sort=True)

    # Remove duplicates, keeping the first computations
    df = df.drop_duplicates(subset="label", keep="first")
    return df


# Convenient helper function to access xyz coordinates from df
def _get_xyz(df, label):
    """Get xyz coordinates from a pandas data frame.

    Parameters
    ----------
    df : pandas.DataFrame
        Data frame with (at least) columns x, y, z, label.
    label : str
        Electrode label for which to get x, y, z from `df`.

    Returns
    -------
    x, y, z : float
        Positions of electrodes on a unit sphere.

    """
    # Check that all labels are present
    for var in ["label", "x", "y", "z"]:
        if var not in df.columns:
            raise ValueError(f"df must contain a column '{var}'")

    # Check we get exactly one row of data
    subdf = df[df["label"] == label]
    nrows = subdf.shape[0]
    if nrows == 0 or nrows > 1:
        raise ValueError(f"Expected one row of data but got: {nrows}")

    # Get the data
    x = float(df[df["label"] == label].x)
    y = float(df[df["label"] == label].y)
    z = float(df[df["label"] == label].z)
    return x, y, z


def _get_coords_on_circle(cx=0, cy=0, r=1, steps=180 / 20):
    """Get the cartesian coordinates [x,y] for a number of points on a circle.

    Assume that top of circle is 0 degrees.

    Parameters
    ----------
    cx, cy : int
        Coordinates (x and y) of origin of circle. Defaults
        to 0 for x and y.
    r : int
        Radius of circle, defaults to 1.
    steps : int
        Spacing between evenly spaced points on the
        circle in degrees. Defaults to 9 (360 degrees
        divided into 40 parts, i.e., 5 percent parts)

    Returns
    -------
    coords : list of list
        Nested list of points: ``[[x1, y1], [x2, y2], ...]``.

    """
    # Make sure we are dealing with integer steps
    assert steps / int(steps) == 1.0
    steps = int(steps)

    coords = []
    for a in np.arange(0, 360, steps):
        x = cx + r * np.cos(np.deg2rad(a))
        y = cy + r * np.sin(np.deg2rad(a))
        coords.append([x, y])

    # Exchange x and y so that 0 degree is top of circle
    # also round off
    coords = [[round(y, 5), round(x, 5)] for x, y in coords]  # noqa

    return coords


def _stereographic_projection(x, y, z, scale=1.0):
    """Calculate the stereographic projection.

    Given a unit sphere with radius ``r = 1`` and center at
    The origin. Project the point ``p = (x, y, z)`` from the
    sphere's South pole ``(0, 0, -1)`` onto a tangent plane
    on the sphere's North pole ``(0, 0, 1)``. The resulting
    point is ``p' = (x', y')``.

    ``x', y' = (1 / (x + z)), (1 / (y + z))``

    Parameters
    ----------
    x, y, z : float
        Positions of electrodes on a unit sphere
    scale : float
        Determines the distance of the projection point
        from the origin of the sphere in terms of the radius.
        Defaults to 1.0, which is a point on the sphere.

    Returns
    -------
    x, y : float
        Positions of electrodes as projected onto a unit circle.

    """
    mu = 1.0 / (scale + z)
    x = x * mu
    y = y * mu
    return np.asarray(x), np.asarray(y)
