"""Test whether the contour labels are complete."""

from eeg_positions.config import (
    ACCEPTED_EQUATORS,
    SYSTEM1005,
    SYSTEM1010,
    SYSTEM1020,
    CONTOUR_ORDER_Nz_EQUATOR,
)


def test_contour_lengths():
    """Check that we have 17 or 21 electrode per contour."""
    for contour in CONTOUR_ORDER_Nz_EQUATOR:
        assert len(contour) in [17, 21]


def test_system_labels():
    """Check if systems have the correct number of labels."""
    assert len(SYSTEM1005) == 345
    assert len(SYSTEM1020) == 21
    assert len(SYSTEM1010) == 71


def test_accepted_equators():
    """We accept two kinds of equators."""
    assert len(ACCEPTED_EQUATORS) == 2
