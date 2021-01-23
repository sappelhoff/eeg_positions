"""
=====================================
Use ``eeg_positions`` with MNE-Python
=====================================

BIDSPath is MNE-BIDS's working horse when it comes to file and folder
operations. Learn here how to use it.

.. currentmodule:: eeg_positions
"""  # noqa: D400 D205
# Copyright (c) 2018-2021, Stefan Appelhoff
# BSD-3-Clause

# %%
# We start with imports

import mne
from eeg_positions import find_point_at_fraction, get_elec_coords

# %% Now we get the positions we want
#
# :func:`find_point_at_fraction`
# :func:`get_elec_coords`

p = find_point_at_fraction((-1, 0, 0),(0, 0, 1) ,(1, 0, 0), 0)
print(p)

# %% Let's make a first plot in 3D

print(mne.__version__)
# %% We can also plot in 2D

coords = get_elec_coords(as_mne_montage=True)
coords.plot()
# %% Note when selecting equator over Fpz and 2D, we may need to adjust
