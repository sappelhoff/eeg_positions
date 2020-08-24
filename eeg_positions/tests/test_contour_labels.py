"""Test whether the contour labels are complete."""
# Copyright (c) 2018-2020, Stefan Appelhoff
# BSD-3-Clause

from eeg_positions.contour_labels import (ALL_CONTOURS, SYSTEM1020, SYSTEM1010,
                                          SYSTEM1005)


def test_contour_lengths():
    """Check that we have 17 or 21 electrode per contour."""
    for contour in ALL_CONTOURS:
        assert len(contour) in [17, 21]


def test_system_labels():
    """Check if systems have the correct number of labels."""
    assert len(SYSTEM1005) == 345
    assert len(SYSTEM1020) == 21
    assert len(SYSTEM1010) == 71
