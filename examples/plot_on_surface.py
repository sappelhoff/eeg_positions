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
# better.
#
# Below we will rotate and translate our montage relative to fsaverage, and scale
# fsaverage along each of its three axes, to minimize the distance of the sensors and
# landmarks (LPA, RPA, NAS) of our montage to the scalp surface.

# sphinx_gallery_thumbnail_number = 3
fiducials = "estimated"  # taken from fsaverage
subject = "fsaverage"

coreg = mne.coreg.Coregistration(info, subject, subjects_dir, fiducials=fiducials)

coreg.set_scale_mode("3-axis")  # can also be "uniform", but the fit would be worse

coreg.fit_fiducials(verbose=True)

coreg.fit_icp(
    n_iterations=100,
    lpa_weight=1.0,
    nasion_weight=1.0,
    rpa_weight=1.0,
    hsp_weight=0,
    eeg_weight=1.0,
    hpi_weight=0,
    verbose=True,
)

# scaling factors along the x (left-right), y (back-front), and z (bottom-top) axes
print(coreg.scale)

# The transform in coreg.trans only contains the rotation and translation.
# The scaling applies to the MRI, so we scale the head surface and the MRI
# landmarks ourselves before plotting.
head_fname = subjects_dir / subject / "bem" / f"{subject}-head.fif"
head = mne.read_bem_surfaces(head_fname)[0]
head["rr"] *= coreg.scale
# surface normals scale inversely; update them so the head is shaded correctly
head["nn"] /= coreg.scale
head["nn"] /= np.linalg.norm(head["nn"], axis=1, keepdims=True)

# copy the landmarks (in MRI coordinates), so that those in coreg remain unscaled
mri_fiducials = coreg.fiducials.copy().dig
for dig_point in mri_fiducials:
    dig_point["r"] *= coreg.scale

fig = mne.viz.plot_alignment(
    info=info,
    trans=coreg.trans,
    subject=subject,
    subjects_dir=subjects_dir,
    bem=[head],  # the scaled head surface
    surfaces={"head": 0.8},  # alpha value
    coord_frame="head",
    eeg=["original", "projected"],
    dig="fiducials",
    show_axes=True,
    # a list of landmark points works here, but is not documented in MNE (as of 1.13)
    mri_fiducials=mri_fiducials,
)

mne.viz.set_3d_view(figure=fig, azimuth=135, elevation=80)

# %%
# The sensors are now close to the scalp, but only after moving the montage relative
# to fsaverage and squashing and stretching fsaverage along its axes (see the scaling
# factors printed above), so it no longer resembles a realistic head. The landmarks of
# the montage and the MRI are also further apart than in the previous plot.
#
# So for actual source reconstruction, you should use sensor positions that are
# measured (digitized), rather than computed on a sphere (idealized).
#
# The 1005 system EEG electrode positions shipped with MNE-Python as "fsaverage_1005"
# were fitted to a realistic head model rather than computed on an idealized sphere,
# so they provide a closer fit on a realistic head surface.
#
# Let's have a look, first in 2D, then in 3D

# Getting the MNE-Python inbuilt 1005 system positions
montage_mne = mne.channels.make_standard_montage(kind="fsaverage_1005")
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
# As is maybe apparent from the plot above, the inbuilt mne montage does not look as
# clear when projected to a spherical 2D head model. The inbuilt ``eeg_positions``
# montage, on the other hand, can really shine in this situation (because that is what
# it was designed for).
#
# Fortunately, the inbuilt mne montage fits the original, unscaled fsaverage head well,
# including the landmarks, see below, and compare to the ``eeg_positions`` fits on
# fsaverage above.

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
