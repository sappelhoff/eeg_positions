[![Python build](https://github.com/sappelhoff/eeg_positions/workflows/Python%20build/badge.svg)](https://github.com/sappelhoff/eeg_positions/actions?query=workflow%3A%22Python+build%22)
[![Python tests](https://github.com/sappelhoff/eeg_positions/workflows/Python%20tests/badge.svg)](https://github.com/sappelhoff/eeg_positions/actions?query=workflow%3A%22Python+tests%22)
[![Test coverage](https://codecov.io/gh/sappelhoff/eeg_positions/branch/main/graph/badge.svg)](https://codecov.io/gh/sappelhoff/eeg_positions)
[![Documentation status](https://readthedocs.org/projects/eeg-positions/badge/?version=latest)](https://eeg-positions.readthedocs.io/en/latest/?badge=latest)
[![PyPi version](https://img.shields.io/pypi/v/eeg_positions.svg)](https://pypi.org/project/eeg_positions/)
[![Conda version](https://img.shields.io/conda/vn/conda-forge/eeg_positions.svg)](https://anaconda.org/conda-forge/eeg_positions)
[![Zenodo archive](https://zenodo.org/badge/136149692.svg)](https://zenodo.org/badge/latestdoi/136149692)

# eeg_positions

Compute and plot standard EEG electrode positions on a spherical head model.

Check out the [**Documentation**](https://eeg-positions.readthedocs.io/en/latest/) for more details.

## Quickstart

There are two common ways to use this repository:

1. Go to the `data/` directory and download the EEG electrode position files you need
   (see the corresponding [README](https://github.com/sappelhoff/eeg_positions/tree/main/data)).

1. Use `eeg_positions` as a Python package (install instructions below),
   and then obtain the EEG electrode positions through the `get_elec_coords` function.
   Check out the [examples](https://eeg-positions.readthedocs.io/en/latest/auto_examples/index.html)
   and [API documentation](https://eeg-positions.readthedocs.io/en/latest/api.html) for more details.

## Installation

To install the **stable** version of `eeg_positions`, use:

`python -m pip install --upgrade eeg_positions`

Or if you use [conda](https://docs.conda.io/en/latest/miniconda.html):

`conda install --channel conda-forge eeg_positions`

To install the **latest development** version of `eeg_positions`, use:

`python -m pip install --upgrade https://github.com/sappelhoff/eeg_positions/archive/refs/heads/main.zip`

## Contributing

The development of `eeg_positions` is taking place on
[GitHub](https://github.com/sappelhoff/eeg_positions).

For more information, please see
[CONTRIBUTING.md](https://github.com/sappelhoff/eeg_positions/blob/main/.github/CONTRIBUTING.md).

## Cite

If you find this repository useful and want to cite it in your work, please go
to the [Zenodo record](https://doi.org/10.5281/zenodo.3718568) and obtain the
appropriate citation from the *"Cite as"* section there.
