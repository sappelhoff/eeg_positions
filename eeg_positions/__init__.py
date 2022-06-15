"""Compute and plot standard EEG electrode positions."""

__version__ = "2.1.0"


from eeg_positions.compute import (
    get_alias_mapping,
    get_available_elec_names,
    get_elec_coords,
)
from eeg_positions.utils import find_point_at_fraction
from eeg_positions.viz import plot_coords

__all__ = (
    "find_point_at_fraction",
    "get_elec_coords",
    "get_available_elec_names",
    "get_alias_mapping",
    "plot_coords",
)
