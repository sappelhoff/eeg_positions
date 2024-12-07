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

# sphinx_gallery_thumbnail_number = 3

# %%
# Make some imports
# This example furthermore assumes that you have installed eeg_positions
# via ``pip install eeg_positions[docs]``
import mne
import numpy as np

from eeg_positions import get_elec_coords

# %%
# Get fsaverage data via MNE-Python, this will download some data
subjects_dir = mne.datasets.fetch_fsaverage().parent

# %%
# Get idealized sensor positions that were computed on a sphere
# and export as mne.DigMontage
montage = get_elec_coords(as_mne_montage=True)

# %%
# For the code below we need to provide an mne.Info object.
# The sampling frequency does not matter so we are setting it to 1.
info = mne.create_info(ch_names=montage.ch_names, sfreq=1, ch_types="eeg")
info.set_montage(montage)

# %%
# As a sanity check, let's create a spherical head model first.
# We expect a perfect fit with our idealized electrode positions.
sphere = mne.make_sphere_model(r0="auto", head_radius="auto", info=info)

trans = mne.Transform("head", "mri", trans=np.eye(4))  # identity transform

fig = mne.viz.plot_alignment(
    info=info,
    trans=trans,
    subject="fsaverage",
    subjects_dir=subjects_dir,
    bem=sphere,
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
# Now let's proceed to plot our positions on the fsaverage head.

trans = "fsaverage"
fig = mne.viz.plot_alignment(
    info=info,
    trans=trans,
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
# get an automatic transformation
fiducials = "estimated"  # taken from fsaverage
subject = "fsaverage"
coreg = mne.coreg.Coregistration(info, subject, subjects_dir, fiducials=fiducials)
coreg.set_scale_mode("3-axis")
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
    trans=trans,
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
