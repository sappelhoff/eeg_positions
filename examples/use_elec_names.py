"""
=======================================
Get specific electrodes and use aliases
=======================================

.. currentmodule:: eeg_positions
"""  # noqa: D400 D205
# Copyright (c) 2018-2021, Stefan Appelhoff
# BSD-3-Clause

# %%
# We need to import some functions

from pprint import pprint

from eeg_positions import (
    get_alias_mapping,
    get_available_elec_names,
    get_elec_coords,
    plot_coords,
)

# %%
# Let's assume we need only a small subset of electrodes for our work.
# We can print all available electrode names in ``eeg_positions``.

elec_names = get_available_elec_names()
pprint(elec_names[::-1])

# %%
# A keen eye may have identified some "odd" electrodes, that are not really part
# of the 10-20, 10-10, or 10-05 systems: ``'A1', 'A2', 'M1', 'M2'``
#
# These are supplied with ``eeg_positions`` for convenience as so-called "alias"
# positions. See below:


alias_mapping = get_alias_mapping()
for key, val in alias_mapping.items():
    print(f"{key}: {val}")

# %%
# We see that for example `A1` is mapped to a position near the left preauricular point
# (LPA). This position is meant to reflect that the A1 electrode is typically a clip-on
# electrode applied to the earlobe.
#
# Similarly, the `M1` electrode is typically applied to the left mastoid on the head of
# a study participant. Its position approximately coincides with the `TP9` position.
#
# **But now back to the topic: We want to get coordinates for a small subset of
# electrodes!**

# Just use `elec_names`
coords = get_elec_coords(
    elec_names=["A1", "A2", "FC3", "CP4", "M1", "LPA", "RPA", "T10"],
    drop_landmarks=False,
    dim="3d",
)

coords.head()

# %%
# Plot it, and see how close LPA and A1 (and RPA and A2) are in space.

fig, ax = plot_coords(coords, text_kwargs=dict(fontsize=10))

ax.axis("off")
fig
