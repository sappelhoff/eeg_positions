"""
=====================================
Use ``eeg_positions`` with MNE-Python
=====================================

.. currentmodule:: eeg_positions
"""  # noqa: D400 D205
# Copyright (c) 2018-2021, Stefan Appelhoff
# BSD-3-Clause

# %%
# We start with imports

from eeg_positions import get_elec_coords

# %%
# Now we get the positions we want

coords = get_elec_coords(as_mne_montage=True)

# coords is an MNE-Python DigMontage object
print(coords)

# %%
# Making use of the :class:`mne.channels.DigMontage` methods, we can visualize
# the electrode positions

coords.plot()

# %% Note when selecting equator over Fpz and 2D, we may need to adjust
