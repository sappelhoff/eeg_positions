"""
==================================
Plot sensors on realistic surfaces
==================================

Sometimes you may want to plot sensor positions on a realistic surface,
like an actual head.
The ``fsaverage`` standard brain template shipped with the Freesurfer
package provides surfaces of the head, so we are going to use them below.

For more information, check out these MNE resources:

- https://mne.tools/dev/auto_examples/visualization/eeg_on_scalp.html
- https://mne.tools/dev/auto_examples/visualization/montage_sgskip.html

.. currentmodule:: eeg_positions
"""  # noqa: D400 D205

# %%
# We start by importing what we need.
#
# This example furthermore assumes that you have installed eeg_positions
# via ``pip install eeg_positions[docs]``.
import matplotlib.pyplot as plt
import mne
import numpy as np

from eeg_positions import get_elec_coords

# %%
# Get fsaverage data via MNE-Python, this will download some data.
subjects_dir = mne.datasets.fetch_fsaverage().parent

# %%
# Get idealized sensor positions that were computed on a sphere
# and export as :class:`mne.channels.DigMontage`.
montage = get_elec_coords(as_mne_montage=True)

# %%
# For the code below we need to provide an :class:`mne.Info` object.
# The sampling frequency does not matter so we are setting it to 1.
info = mne.create_info(ch_names=montage.ch_names, sfreq=1, ch_types="eeg")
info.set_montage(montage)

# %%
# As a sanity check, let's create a spherical head model first.
# We expect a perfect fit with our idealized electrode positions,
# because they were also computed on a sphere.
sphere = mne.make_sphere_model(r0="auto", head_radius="auto", info=info)

# We need a transform from the coordinates of our montage to the surface.
# Given that both are spheres, we do not need to actually transform, and
# can just use the identity transform.
trans = mne.Transform("head", "mri", trans=np.eye(4))

fig = mne.viz.plot_alignment(
    info=info,
    trans=trans,
    bem=sphere,  # our spherical head model
    surfaces={"head": 0.8},  # alpha value
    coord_frame="head",
    eeg=["original", "projected"],
    dig="fiducials",
    show_axes=True,
    mri_fiducials=False,
)

mne.viz.set_3d_view(figure=fig, azimuth=65, elevation=75)

# %%
# As can be seen above, the fit of our idealized sensor positions with a spherical head
# model is perfect.
#
# Now let's proceed to plot our positions on the fsaverage head.
# We expect this to be potentially problematic, because we computed our positions
# on a sphere ... and a sphere is usually a poor approximation of a human head.

# instead of the identity transform as above, we are using the inbuilt transformation
# from MNE-Python that can transform a Montage to fit fsaverage.
# Note that this only works for "fsaverage" and not other surfaces.
trans = "fsaverage"

fig = mne.viz.plot_alignment(
    info=info,
    trans=trans,
    subject="fsaverage",  # this is fsaverage
    subjects_dir=subjects_dir,  # directory of fsaverage
    surfaces={"head": 0.8},  # alpha value
    coord_frame="head",
    eeg=["original", "projected"],
    dig="fiducials",
    show_axes=True,
    mri_fiducials=True,
)

mne.viz.set_3d_view(figure=fig, azimuth=135, elevation=80)

# %%
# As expected, the fit above is very poor.
#
# The electrode positions that were computed on a sphere are not easily projected
# to the fsaverage head.
#
# However, we can try to "scale" fsaverage in three dimensions to make the fit
# slightly better.
#
# Below we will try to scale fsaverage to minimize the distance of sensors to the scalp
# surface, while still trying to have the landmarks (LPA, RPA, NAS) aligned between MRI
# and montage.

# sphinx_gallery_thumbnail_number = 3
fiducials = "estimated"  # taken from fsaverage
subject = "fsaverage"

coreg = mne.coreg.Coregistration(info, subject, subjects_dir, fiducials=fiducials)

coreg.set_scale_mode("3-axis")  # can also be "uniform", but the fit would be worse

coreg.fit_fiducials(verbose=True)

coreg.fit_icp(
    n_iterations=40,
    lpa_weight=1.0,
    nasion_weight=1.0,
    rpa_weight=1.0,
    hsp_weight=0,
    eeg_weight=1.0,
    hpi_weight=0,
    verbose=True,
)
trans = coreg.trans

fig = mne.viz.plot_alignment(
    info=info,
    trans=trans,  # this is the optimized transform based on scaling fsaverage
    subject="fsaverage",
    subjects_dir=subjects_dir,
    surfaces={"head": 0.8},  # alpha value
    coord_frame="head",
    eeg=["original", "projected"],
    dig="fiducials",
    show_axes=True,
    mri_fiducials=True,
)

mne.viz.set_3d_view(figure=fig, azimuth=135, elevation=80)

# %%
# Luckily, the fit is now slightly better.
#
# It is still not perfect, so for actual source reconstruction, you should use sensor
# positions that are measured (digitized), rather than computed on a sphere
# (idealized).
#
# The 1005 system eeg electrode positions shipped with MNE-Python happen to not be
# calculated on a sphrere (idealized), so they should be a better fit on a realistic
# surface.
#
# Let's have a look, first in 2D, then in 3D

# Getting the MNE-Python inbuilt 1005 system positions
montage_mne = mne.channels.make_standard_montage(kind="standard_1005")
info_mne = mne.create_info(ch_names=montage_mne.ch_names, sfreq=1, ch_types="eeg")
info_mne.set_montage(montage_mne)

# Plot in 2D versus the eeg_positions montage
fig, axs = plt.subplots(1, 2)
fig.set_layout_engine("constrained")

for i, this_info in enumerate([info, info_mne]):
    ax = axs.flat[i]
    this_info.plot_sensors(axes=ax, show=False)
    ax.set_title(["eeg_positions", "mne inbuilt"][i])

fig
# %%
# As is maybe apparent from the plot above, the inbuilt mne 1005 montage does not
# look as clear when projected to a spherical 2D head model. The inbuilt
# ``eeg_positions`` montage, on the other hand, can really shine in this situation
# (because that is what it was designed for).
#
# Fortuntely, the inbuilt mne montage will give us a much better fit on a realistic
# surface, see below, and compare to the two plots above.

trans = "fsaverage"

fig = mne.viz.plot_alignment(
    info=info_mne,
    trans=trans,
    subject="fsaverage",  # this is fsaverage
    subjects_dir=subjects_dir,  # directory of fsaverage
    surfaces={"head": 0.8},  # alpha value
    coord_frame="head",
    eeg=["original", "projected"],
    dig="fiducials",
    show_axes=True,
    mri_fiducials=True,
)

mne.viz.set_3d_view(figure=fig, azimuth=135, elevation=80)

# %%
