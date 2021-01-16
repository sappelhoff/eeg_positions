"""Initialize eeg_positions."""
# Copyright (c) 2018-2021, Stefan Appelhoff
# BSD-3-Clause

__version__ = "1.1.0.dev0"


from eeg_positions.compute import get_elec_coords
from eeg_positions.utils import find_point_at_fraction

__all__ = (
    "find_point_at_fraction",
    "get_elec_coords",
)
