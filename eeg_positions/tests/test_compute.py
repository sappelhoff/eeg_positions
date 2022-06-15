"""Test the compute module."""

import itertools
import sys
from unittest import mock

import pytest

from eeg_positions.compute import (
    _produce_files_and_do_x,
    get_available_elec_names,
    get_elec_coords,
)

valid_inputs = itertools.product(
    ("1020", "1010", "1005"),
    (None, ["Cz"], ["A1", "M1"]),
    (True, False),
    ("2d", "3d"),
    (True, False),
    ("Nz-T10-Iz-T9", "Fpz-T8-Oz-T7"),
    (True, False),
)


@pytest.mark.parametrize(
    "system, elec_names, drop_landmarks, dim, as_mne_montage, equator, sort",
    valid_inputs,
)
def test_get_elec_coords(
    system, elec_names, drop_landmarks, dim, as_mne_montage, equator, sort
):
    """Smoke test the get_elec_coords function."""
    get_elec_coords(
        system=system,
        elec_names=elec_names,
        drop_landmarks=drop_landmarks,
        dim=dim,
        as_mne_montage=as_mne_montage,
        equator=equator,
        sort=sort,
    )


def test_get_elec_coords_io():
    """Test bad inputs to get_elec_coords."""
    match = "`equator` must be one of"
    with pytest.raises(ValueError, match=match):
        get_elec_coords(equator="Cz")

    match = "`system` must be one of"
    with pytest.raises(ValueError, match=match):
        get_elec_coords(system="1030")

    match = "`elec_names` must be a list of str or None."
    with pytest.raises(ValueError, match=match):
        get_elec_coords(elec_names="Cz")

    match = "For some `elec_names` there are no available positions"
    with pytest.raises(ValueError, match=match):
        get_elec_coords(elec_names=["bogus"])

    match = "`dim` must be one of"
    with pytest.raises(ValueError, match=match):
        get_elec_coords(dim="4d")

    match = "must be a boolean value, but found"
    with pytest.raises(ValueError, match=match):
        get_elec_coords(as_mne_montage="False")

    match = "must be a boolean value, but found"
    with pytest.raises(ValueError, match=match):
        get_elec_coords(drop_landmarks="True")

    match = "You specified the same electrode position using two aliases"
    with pytest.raises(ValueError, match=match):
        get_elec_coords(elec_names=["M1", "TP9"])

    # check coords order
    elec_names = ["Fp1", "AFz"]
    coords = get_elec_coords(elec_names=elec_names)  # default sort=False
    assert coords.label.to_list() == elec_names
    coords = get_elec_coords(elec_names=elec_names, sort=False)
    assert coords.label.to_list() == elec_names
    coords = get_elec_coords(elec_names=elec_names, sort=True)
    assert coords.label.to_list() == sorted(elec_names)

    # Mock a too-low version of mne
    mock_mne = mock.MagicMock()
    mock_mne.__version__ = "0.19.0"
    sys.modules["mne"] = mock_mne
    match = ".*update your mne.* but you have 0.19.0."
    with pytest.raises(RuntimeError, match=match):
        get_elec_coords(as_mne_montage=True)
    del sys.modules["mne"]

    # mock mne not present at all
    sys.modules["mne"] = None
    match = "if `as_mne_montage` is True, you must have mne installed."
    with pytest.raises(ImportError, match=match):
        get_elec_coords(as_mne_montage=True)
    del sys.modules["mne"]


def test_get_available_elec_names():
    """Test get_available_elec_names."""
    match = "Unknown input for `system`: bogus"
    with pytest.raises(ValueError, match=match):
        get_available_elec_names(system="bogus")


def test_produce_files_and_do_x():
    """Test the data that we ship is as expected."""
    _produce_files_and_do_x(x="compare")
    _produce_files_and_do_x(x="save")
