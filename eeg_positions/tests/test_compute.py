"""Test the compute module."""
# Copyright (c) 2018-2021, Stefan Appelhoff
# BSD-3-Clause
import itertools

import pytest

from eeg_positions.compute import get_elec_coords

valid_inputs = itertools.product(
    ("1020", "1010", "1005"),
    (None, ["Cz"]),
    (True, False),
    ("2d", "3d"),
    (True, False),
    ("Nz-T10-Iz-T9", "Fpz-T8-Oz-T7"),
)


@pytest.mark.parametrize(
    "system, elec_names, drop_landmarks, dim, as_mne_montage, equator", valid_inputs
)
def test_get_elec_coords(
    system, elec_names, drop_landmarks, dim, as_mne_montage, equator
):
    """Smoke test the get_elec_coords function."""
    get_elec_coords(
        system=system,
        elec_names=elec_names,
        drop_landmarks=drop_landmarks,
        dim=dim,
        as_mne_montage=as_mne_montage,
        equator=equator,
    )
