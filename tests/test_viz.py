"""Test the visualization functions."""

import matplotlib
import pandas as pd
import pytest

from eeg_positions import get_elec_coords, plot_coords
from eeg_positions.viz import _plot_2d_head, _plot_spherical_head

# No-display backend for tests
matplotlib.use("agg")


def test_plot_spherical_head():
    """Very basic test whether calling the function throws an error."""
    fig, ax = _plot_spherical_head()


def test_plot_2d_head():
    """Very basic test whether calling the function throws an error."""
    fig, ax = _plot_2d_head()


def test_plot_coords():
    """Test plot_coords."""
    with pytest.raises(ValueError, match="`coords` must be a pandas DataFrame object."):
        plot_coords([1, 2, 3])

    with pytest.raises(
        ValueError, match=f"`coords` does not have a required column {'y'}."
    ):
        plot_coords(pd.DataFrame(columns=["label", "x"]))

    coords = get_elec_coords()
    fig, ax = plot_coords(coords)
    fig, ax = plot_coords(coords[["label", "x", "y"]])

    # Test cEEGrid
    coords_ceegrid_3d = get_elec_coords(system="ceegrid", dim="3d")
    fig, ax = plot_coords(coords_ceegrid_3d)
    coords_ceegrid_2d = get_elec_coords(system="ceegrid", dim="2d")
    fig, ax = plot_coords(coords_ceegrid_2d)
