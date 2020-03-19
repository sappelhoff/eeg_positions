"""Test the utility functions."""

from eeg_positions.utils import (get_xyz, find_point_at_fraction,
                                 plot_spherical_head, plot_2d_head,
                                 stereographic_projection)

import pytest
import numpy as np
import matplotlib
import pandas as pd

# No-display backend for tests
matplotlib.use('agg')


def test_get_xyz():
    """Check whether we can get xyz coordinates."""
    # Test the expected case
    data = {'label': ['Cz', 'Pz'],
            'x': [1, 2],
            'y': [2, 3],
            'z': [3, 4]}
    df = pd.DataFrame(data)
    x, y, z = get_xyz(df, 'Cz')
    assert x == 1 and y == 2 and z == 3
    x, y, z = get_xyz(df, 'Pz')
    assert x == 2 and y == 3 and z == 4

    # Test that a non-present label is inquired
    with pytest.raises(ValueError):
        get_xyz(df, 'f')

    # Test data frame has insufficient columns
    with pytest.raises(ValueError):
        data = {'elec': '[Oz]', 'az': [2], 'po': [1]}
        df = pd.DataFrame(data)
        get_xyz(df, 'Oz')

    # Test there are duplicates
    with pytest.raises(ValueError):
        data = {'label': ['Cz', 'Cz'],
                'x': [1, 2],
                'y': [2, 3],
                'z': [3, 4]}
        df = pd.DataFrame(data)
        get_xyz(df, 'f')


def test_find_point_at_fraction():
    """Test the assumptions of the fraction point finder."""
    # Test the general assumptions for fraction 0, 1, 0.5
    p1 = (1., 0., 0.)
    p2 = (0., 0., 1.)
    p3 = (-1., 0., 0.)
    point = find_point_at_fraction(p1, p2, p3, frac=0.)
    assert point == p1
    point = find_point_at_fraction(p1, p2, p3, frac=1.)
    assert point == p3
    point = find_point_at_fraction(p1, p2, p3, frac=0.5)
    assert point == p2

    # Assert error when equal points
    with pytest.raises(ValueError):
        find_point_at_fraction(p1, p1, p3, frac=0.5)


def test_stereographic_projection():
    """Test the stereographic projection."""
    data = {'label': ['Cz', 'Nz'],
            'x': [0, 0],
            'y': [0, 1],
            'z': [1, 0]}
    df = pd.DataFrame(data)

    # We know where Cz and Nz should be in 2D:
    xs, ys = stereographic_projection(df['x'], df['y'], df['z'])
    np.testing.assert_allclose(xs, np.array((0, 0)))
    np.testing.assert_allclose(ys, np.array((0, 1)))


def test_plot_spherical_head():
    """Very basic test whether calling the function throws an error."""
    fig, ax = plot_spherical_head()
    assert fig is not None
    assert ax is not None


def test_plot_2d_head():
    """Very basic test whether calling the function throws an error."""
    fig, ax = plot_2d_head()
    assert fig is not None
    assert ax is not None
