"""Test the utility functions."""
# Copyright (c) 2018-2021, Stefan Appelhoff
# BSD-3-Clause

import numpy as np
import pandas as pd
import pytest

from eeg_positions.utils import (
    _add_points_along_contour,
    _get_xyz,
    _stereographic_projection,
    find_point_at_fraction,
)


def test_get_xyz():
    """Check whether we can get xyz coordinates."""
    # Test the expected case
    data = {"label": ["Cz", "Pz"], "x": [1, 2], "y": [2, 3], "z": [3, 4]}
    df = pd.DataFrame(data)
    x, y, z = _get_xyz(df, "Cz")
    assert x == 1 and y == 2 and z == 3
    x, y, z = _get_xyz(df, "Pz")
    assert x == 2 and y == 3 and z == 4

    # Test that a non-present label is inquired
    with pytest.raises(ValueError):
        _get_xyz(df, "f")

    # Test data frame has insufficient columns
    with pytest.raises(ValueError):
        data = {"elec": "[Oz]", "az": [2], "po": [1]}
        df = pd.DataFrame(data)
        _get_xyz(df, "Oz")

    # Test there are duplicates
    with pytest.raises(ValueError):
        data = {"label": ["Cz", "Cz"], "x": [1, 2], "y": [2, 3], "z": [3, 4]}
        df = pd.DataFrame(data)
        _get_xyz(df, "f")


def test_find_point_at_fraction():
    """Test the assumptions of the fraction point finder."""
    # Test the general assumptions for fraction 0, 1, 0.5
    p1 = (1.0, 0.0, 0.0)
    p2 = (0.0, 0.0, 1.0)
    p3 = (-1.0, 0.0, 0.0)
    p4 = (0.0, 0.0, -1.0)
    point = find_point_at_fraction(p1, p2, p3, frac=0.0)
    assert point == p1
    point = find_point_at_fraction(p1, p2, p3, frac=1.0)
    assert point == p3
    point = find_point_at_fraction(p1, p2, p3, frac=0.5)
    assert point == p2

    # Assert error when equal points
    with pytest.raises(ValueError):
        find_point_at_fraction(p1, p1, p3, frac=0.5)

    # Test some extreme fractions
    point = find_point_at_fraction(p1, p2, p3, frac=1.5)
    assert point == p4
    point = find_point_at_fraction(p1, p2, p3, frac=2.0)
    assert point == p1
    point = find_point_at_fraction(p1, p2, p3, frac=2.5)
    assert point == p2

    # stretch how far points are apart
    # NOTE: better draw on a sheet to see why these numbers make sense
    pstar = find_point_at_fraction(p1, p2, p3, frac=0.75)
    point = find_point_at_fraction(p1, pstar, p4, frac=2 / 6)
    assert point == p2
    point = find_point_at_fraction(p1, pstar, p4, frac=4 / 6)
    assert point == p3


def test_add_points_along_contour():
    """Test _add_points_along_contour."""
    fake_contour = list(range(40))
    match = "contour must be of len 17 or 21 but is 40"
    with pytest.raises(ValueError, match=match):
        _add_points_along_contour("fake_df", fake_contour)


def test_stereographic_projection():
    """Test the stereographic projection."""
    data = {"label": ["Cz", "Nz"], "x": [0, 0], "y": [0, 1], "z": [1, 0]}
    df = pd.DataFrame(data)

    # We know where Cz and Nz should be in 2D:
    xs, ys = _stereographic_projection(df["x"], df["y"], df["z"])
    np.testing.assert_allclose(xs, np.array((0, 0)))
    np.testing.assert_allclose(ys, np.array((0, 1)))
