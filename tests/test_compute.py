"""Test the compute module."""

import itertools
import sys

import numpy as np
import pandas as pd
import pytest

from eeg_positions.compute import (
    _produce_files_and_do_x,
    get_alias_mapping,
    get_available_elec_names,
    get_elec_coords,
)

valid_inputs = list(
    itertools.product(
        ("1020", "1010", "1005"),
        (None, ["Cz"], ["A1", "M1"]),
        (True, False),
        ("2d", "3d"),
        (True, False),
        ("Nz-T10-Iz-T9", "Fpz-T8-Oz-T7"),
        (True, False),
    )
)


@pytest.mark.parametrize(
    "system, elec_names, drop_landmarks, dim, as_mne_montage, equator, sort",
    valid_inputs,
)
def test_get_elec_coords(
    system, elec_names, drop_landmarks, dim, as_mne_montage, equator, sort
):
    """Smoke test the get_elec_coords function."""
    out = get_elec_coords(
        system=system,
        elec_names=elec_names,
        drop_landmarks=drop_landmarks,
        dim=dim,
        as_mne_montage=as_mne_montage,
        equator=equator,
        sort=sort,
    )

    if not as_mne_montage:
        # out is pd.DataFrame, assert there are no NaNs in any cell
        assert (out.isnull().sum() == 0).all()


valid_ceegrid_inputs = list(
    itertools.product(
        (None, ["ceegrid_L01"], ["L01", "R08"], ["L1", "R8"]),
        (True, False),
        ("2d", "3d"),
        (True, False),
        ("Nz-T10-Iz-T9", "Fpz-T8-Oz-T7"),
        (True, False),
    )
)


@pytest.mark.parametrize(
    "elec_names, drop_landmarks, dim, as_mne_montage, equator, sort",
    valid_ceegrid_inputs,
)
def test_get_elec_coords_ceegrid(
    elec_names, drop_landmarks, dim, as_mne_montage, equator, sort
):
    """Smoke test cEEGrid with get_elec_coords."""
    out = get_elec_coords(
        system="ceegrid",
        elec_names=elec_names,
        drop_landmarks=drop_landmarks,
        dim=dim,
        as_mne_montage=as_mne_montage,
        equator=equator,
        sort=sort,
    )
    if not as_mne_montage:
        assert (out.isnull().sum() == 0).all()
        if elec_names is None:
            expected_len = 20 if drop_landmarks else 23
            assert len(out) == expected_len


def test_ceegrid_case_insensitivity():
    """Test case insensitivity for cEEGrid system parameter."""
    df_lower = get_elec_coords(system="ceegrid", dim="3d")
    df_mixed = get_elec_coords(system="cEEGrid", dim="3d")
    pd.testing.assert_frame_equal(df_lower, df_mixed)

    names_lower = get_available_elec_names(system="ceegrid")
    names_mixed = get_available_elec_names(system="cEEGrid")
    assert names_lower == names_mixed


def test_ceegrid_alias_mapping():
    """Test alias mapping for cEEGrid electrodes."""
    aliases = get_alias_mapping()
    # Check that padded and unpadded names exist in alias mapping
    for ch in ["01", "02", "03", "04", "04a", "04b", "05", "06", "07", "08"]:
        assert aliases[f"L{ch}"] == f"ceegrid_L{ch}"
        assert aliases[f"R{ch}"] == f"ceegrid_R{ch}"
        unpadded = ch.lstrip("0")
        if unpadded != ch:
            assert aliases[f"L{unpadded}"] == f"ceegrid_L{ch}"
            assert aliases[f"R{unpadded}"] == f"ceegrid_R{ch}"

    # Requesting via alias returns user-requested labels
    coords = get_elec_coords(elec_names=["L01", "R08"], dim="3d")
    assert coords.label.to_list() == ["L01", "R08"]

    # Coordinates match canonical name
    coords_canonical = get_elec_coords(
        elec_names=["ceegrid_L01", "ceegrid_R08"], dim="3d"
    )
    np.testing.assert_allclose(
        coords[["x", "y", "z"]].to_numpy(),
        coords_canonical[["x", "y", "z"]].to_numpy(),
    )


def test_ceegrid_unit_sphere_and_symmetry():
    """Test that all cEEGrid 3D positions lie on the unit sphere and are symmetric."""
    for equator in ["Nz-T10-Iz-T9", "Fpz-T8-Oz-T7"]:
        coords = get_elec_coords(
            system="ceegrid", drop_landmarks=True, dim="3d", equator=equator
        )
        assert len(coords) == 20

        # Every point lies on unit sphere
        r_sq = coords["x"] ** 2 + coords["y"] ** 2 + coords["z"] ** 2
        np.testing.assert_allclose(r_sq, 1.0, atol=1e-5)

        # Symmetry: left and right ear electrodes have x_R = -x_L, y_R = y_L, z_R = z_L
        for ch in ["01", "02", "03", "04", "04a", "04b", "05", "06", "07", "08"]:
            row_l = coords[coords["label"] == f"ceegrid_L{ch}"].iloc[0]
            row_r = coords[coords["label"] == f"ceegrid_R{ch}"].iloc[0]
            assert np.isclose(row_r["x"], -row_l["x"])
            assert np.isclose(row_r["y"], row_l["y"])
            assert np.isclose(row_r["z"], row_l["z"])


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
