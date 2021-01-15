"""Test plotting the coordinate data with MNE-Python."""
# Copyright (c) 2018-2021, Stefan Appelhoff
# BSD-3-Clause

import os

import mne
import numpy as np
import pandas as pd


def test_mne_plotting():
    """Read saved coordinate data and turn into montage."""
    # assume that we saved this file before through running calc_positions.py
    fpath = os.path.dirname(os.path.realpath(__file__))
    fname_template = os.path.join(fpath, "..", "..", "data", "standard_{}.tsv")
    fname = fname_template.format("1005")

    # Now read it
    df = pd.read_csv(fname, sep="\t")

    # Turn data into montage
    ch_pos = df.set_index("label").to_dict("index")
    for key, val in ch_pos.items():
        ch_pos[key] = np.asarray(list(val.values()))

    data = mne.utils.Bunch(
        nasion=ch_pos["Nz"],
        lpa=ch_pos["T9"],
        rpa=ch_pos["T10"],
        ch_pos=ch_pos,
        coord_frame="unknown",
        hsp=None,
        hpi=None,
    )

    montage = mne.channels.make_dig_montage(**data)

    # plot it, using kind="topomap" for 2D, or kind="3d" for 3D
    montage.plot(kind="topomap", sphere=(0, 0, 0, 1))
