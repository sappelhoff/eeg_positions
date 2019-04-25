"""Test whether the contour labels are complete."""

from eeg_positions.contour_labels import (all_contours, system1020, system1010,
                                          system1005)


def test_contour_lengths():
    """Check that we have 17 or 21 electrode per contour."""
    for contour in all_contours:
        assert len(contour) in [17, 21]


def test_system_labels():
    """Check if systems have the correct number of labels."""
    assert len(system1005) == 345
    assert len(system1020) == 21
    assert len(system1010) == 71


if __name__ == '__main__':
    print(all_contours)
