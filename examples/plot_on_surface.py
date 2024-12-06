"""
==================================
Plot sensors on realistic surfaces
==================================

.. currentmodule:: eeg_positions
"""  # noqa: D400 D205

# %%
import mne
import numpy as np

from eeg_positions import get_elec_coords

# %%
# Get fsaverage data via MNE-Python
subjects_dir = mne.datasets.fetch_fsaverage().parent

# Get idealized sensor positions
montage = get_elec_coords(as_mne_montage=True)

info = mne.create_info(ch_names=montage.ch_names, sfreq=1, ch_types="eeg")
info.set_montage(montage)

# %%
# Plot

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
sphere = mne.make_sphere_model(r0="auto", head_radius="auto", info=info)

trans = mne.Transform("head", "mri", trans=np.eye(4))  # identity

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
