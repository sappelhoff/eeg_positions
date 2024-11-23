[![Python build](https://github.com/sappelhoff/eeg_positions/workflows/Python%20build/badge.svg)](https://github.com/sappelhoff/eeg_positions/actions?query=workflow%3A%22Python+build%22)
[![Python tests](https://github.com/sappelhoff/eeg_positions/workflows/Python%20tests/badge.svg)](https://github.com/sappelhoff/eeg_positions/actions?query=workflow%3A%22Python+tests%22)
[![Test coverage](https://codecov.io/gh/sappelhoff/eeg_positions/branch/main/graph/badge.svg)](https://codecov.io/gh/sappelhoff/eeg_positions)
[![Documentation status](https://readthedocs.org/projects/eeg_positions/badge/?version=stable)](https://eeg_positions.readthedocs.io/en/stable/?badge=stable)
[![Latest PyPI release](https://img.shields.io/pypi/v/eeg_positions.svg)](https://pypi.org/project/eeg_positions/)
[![Zenodo archive](https://zenodo.org/badge/136149692.svg)](https://zenodo.org/badge/latestdoi/136149692)

# eeg_positions

Compute and plot standard EEG electrode positions.

Please see the [**Documentation**](https://eeg_positions.readthedocs.io/en/stable/).

## Quickstart

There are two common ways to make use of this repository:

1. Go to the `data/` directory and download the EEG electrode position files you need
   (see the [README](https://github.com/sappelhoff/eeg_positions/tree/main/data) there).

1. Use `eeg_positions` as a Python package (install through `pip install eeg_positions`),
   and then obtain the EEG electrode positions through the `get_elec_coords` function.
   See the [Examples](https://stefanappelhoff.com/eeg_positions/auto_examples/index.html)
   and [API documentation](https://stefanappelhoff.com/eeg_positions/api.html).

## Cite

If you find this repository useful and want to cite it in your work, please go
to the [Zenodo record](https://doi.org/10.5281/zenodo.3718568) and obtain the
appropriate citation from the *"Cite as"* section there.
