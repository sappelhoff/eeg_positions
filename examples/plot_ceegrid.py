"""
================================
Plot cEEGrid electrode positions
================================

The cEEGrid is a flexible printed electrode array placed around the ear
to record unobtrusive ear-EEG (Debener et al., 2015; Bleichner & Debener, 2017).

For more information, see:
- https://gitlab.com/mgbleichner/ceegridplugin
- https://uol.de/psychologie/abteilungen/ceegrid

.. currentmodule:: eeg_positions
"""  # noqa: D400 D205

# %%
# We start by importing the functions we need:

from eeg_positions import get_elec_coords, plot_coords

# %%
# Get idealized 3D coordinates for the 20 cEEGrid electrodes (10 per ear):

coords = get_elec_coords(system="ceegrid", dim="3d")
coords.head()

# %%
# Plot the sensor positions in 3D around the ears:

fig, ax = plot_coords(coords, text_kwargs=dict(fontsize=8))
fig

# %%
# Coordinates can also be projected to 2D:

coords_2d = get_elec_coords(system="ceegrid", dim="2d")
fig, ax = plot_coords(coords_2d, text_kwargs=dict(fontsize=8))
fig

# %%
# Hardware naming conventions like ``L01`` or ``R01`` are supported as aliases:

coords_alias = get_elec_coords(elec_names=["L01", "L02", "R01", "R02"])
coords_alias

# %%
# Export directly to an MNE-Python :class:`mne.channels.DigMontage`:

montage = get_elec_coords(system="ceegrid", as_mne_montage=True)
fig = montage.plot(kind="3d")
fig.gca().view_init(azim=70, elev=15)

# %%
# Comparison to 10-05 scalp electrodes
# ------------------------------------
# While some cEEGrid positions roughly correspond to 10-05 scalp electrodes
# near the ear (e.g., ``ceegrid_L01`` ≈ ``FT9h``, ``ceegrid_L04`` ≈ ``TP9h``),
# standard 10-05 montages do not have electrodes below the equator (such as
# ``ceegrid_L06`` or ``ceegrid_L07``). Dedicated cEEGrid coordinates provide
# the appropriate geometry around the ear.
