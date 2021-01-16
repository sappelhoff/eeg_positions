"""Test the visualization functions."""
# Copyright (c) 2018-2021, Stefan Appelhoff
# BSD-3-Clause

import matplotlib

from eeg_positions.viz import _plot_2d_head, _plot_spherical_head

# No-display backend for tests
matplotlib.use("agg")


def test_plot_spherical_head():
    """Very basic test whether calling the function throws an error."""
    fig, ax = _plot_spherical_head()
    assert fig is not None
    assert ax is not None


def test_plot_2d_head():
    """Very basic test whether calling the function throws an error."""
    fig, ax = _plot_2d_head()
    assert fig is not None
    assert ax is not None
