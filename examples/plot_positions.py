"""
========================
Plot electrode positions
========================

.. currentmodule:: eeg_positions
"""  # noqa: D400 D205
# Copyright (c) 2018-2021, Stefan Appelhoff
# BSD-3-Clause

# %%
# We need to import some functions.

from eeg_positions import get_elec_coords, plot_coords

# %%
# Get the electrode positions!
# Let's start with the basic 10-20 system in 2 dimensions (``"x"`` and ``"y"``).

coords = get_elec_coords(
    system="1020",
    dim="2d",
)

# `coords` is a pandas.DataFrame object
coords.head()

# %%
# Now let's plot these coordinates.
# We can supply some style arguments to :func:`eeg_positions.plot_coords` to control
# the color of the scatter dots, and the text annotations.

fig, ax = plot_coords(
    coords, scatter_kwargs=dict(color="green"), text_kwargs=dict(fontsize=10)
)

ax.axis("off")
fig

# %%
# Notice in the above plot, that the "landmarks" are there: ``NAS``, ``LPA``,
# and ``RPA``. We can drop these by passing the ``drop_landmarks=True`` to
# :func:`get_elec_coords`.

coords = get_elec_coords(
    system="1020",
    drop_landmarks=True,
    dim="2d",
)


fig, ax = plot_coords(
    coords, scatter_kwargs=dict(color="green"), text_kwargs=dict(fontsize=10)
)

ax.axis("off")
fig

# %%
# We can also plot in 3D. Let's pick a system with more electrodes now.

coords = get_elec_coords(
    system="1010",
    drop_landmarks=True,
    dim="3d",
)


fig, ax = plot_coords(coords, text_kwargs=dict(fontsize=7))

fig

# %%
# When using these commands from an interactive Python session, try to set
# the Ipython magic `%matplotlib qt`, which will allow you to freely view the 3d
# plot and rotate the camera.
