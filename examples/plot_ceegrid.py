"""
================================
Plot cEEGrid electrode positions
================================

The cEEGrid is a flexible printed electrode array placed around the ear
to record unobtrusive ear-EEG (Debener et al., 2015; Bleichner & Debener, 2017).

The idealized spherical electrode positions in ``eeg_positions`` are based on the
BESA spherical coordinates from Martin Bleichner's cEEGrid EEGLAB plugin
(``elec_cEEGrid.elp``; Bleichner & Debener, 2017). Coronal angles span 92° to 132°
(midpoint 112°, matching the ear in the ``Fpz-T8-Oz-T7`` equator system) and are
shifted by 22° for the default ``Nz-T10-Iz-T9`` equator to center the array
symmetrically around the preauricular points (LPA and RPA at z = 0).

For more information, see:

- https://gitlab.com/mgbleichner/ceegridplugin
- https://uol.de/psychologie/abteilungen/ceegrid

.. currentmodule:: eeg_positions
"""  # noqa: D400 D205

# %%
# We start by importing the functions we need:

from eeg_positions import get_elec_coords, plot_coords

# %%
# Idealized 3D coordinates can be obtained using ``system="ceegrid"``.
# Canonical names use the ``ceegrid_`` prefix to avoid namespace collisions.
# To keep sensor labels short and readable in plots, we can request
# the electrodes using their short alias names (e.g., ``L01``, ``R01``):

ch_names = [f"L{i:02d}" for i in range(1, 9)] + ["L04a", "L04b"]
ch_names += [f"R{i:02d}" for i in range(1, 9)] + ["R04a", "R04b"]

coords_3d = get_elec_coords(elec_names=ch_names, dim="3d")
coords_3d.head()

# %%
# Plot the sensor positions in 3D around the ears:

fig, ax = plot_coords(coords_3d, text_kwargs=dict(fontsize=8, ha="center"))
fig

# %%
# Coordinates can also be projected to 2D.
#
# Note that stereographic projection from 3D to 2D inevitably brings geometric
# distortion. Because the cEEGrid curves around the ear and its inferior electrodes
# (L06–L08, R06–R08) sit below the equator, they flare outward beyond the head
# shape in 2D. This is normal and expected for sub-equatorial positions.
# For source modeling or anatomical analysis, the 3D coordinates should be used.

coords_2d = get_elec_coords(elec_names=ch_names, dim="2d")
fig, ax = plot_coords(coords_2d, text_kwargs=dict(fontsize=6, ha="left", va="bottom"))
fig

# %%
# We can also export directly to an MNE-Python :class:`mne.channels.DigMontage`,
# preserving the short channel names:

montage = get_elec_coords(elec_names=ch_names, as_mne_montage=True)
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
