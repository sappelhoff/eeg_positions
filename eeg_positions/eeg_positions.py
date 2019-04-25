"""Calculate all standard electrode positions.

See README for information about assumptions.
"""
# Copyright (c) 2018, Stefan Appelhoff
# BSD-3-Clause

from utils import (get_xyz, find_point_at_fraction, plot_spherical_head,
                   plot_2d_head, stereographic_projection)

from contour_labels import all_contours, system1020, system1010, system1005

import pandas as pd
import matplotlib

matplotlib.use('GTK')
import matplotlib.pyplot as plt  # noqa


if __name__ == '__main__':

    # Known locations
    # ---------------
    Nz = (0., 1., 0.)
    Iz = (0., -1., 0.)
    Cz = (0., 0., 1.)
    T9 = (-1., 0., 0.)
    T10 = (1., 0., 0.)

    d = {'label': ['Nz', 'Iz', 'Cz', 'T9', 'T10'],
         'x': [Nz[0], Iz[0], Cz[0], T9[0], T10[0]],
         'y': [Nz[1], Iz[1], Cz[1], T9[1], T10[1]],
         'z': [Nz[2], Iz[2], Cz[2], T9[2], T10[2]]}

    df = pd.DataFrame.from_dict(d)

    # Calculate all positions
    # -----------------------
    for contour in all_contours:

        if len(contour) == 21:
            midpoint_idx = 10
        elif len(contour) == 17:
            midpoint_idx = 8
        else:
            raise ValueError('contour must be of len '
                             '17 or 21 but is {}'.format(len(contour)))

        # Get the reference points from data frame
        p1 = get_xyz(df, contour[0])
        p2 = get_xyz(df, contour[midpoint_idx])
        p3 = get_xyz(df, contour[-1])

        # Calculate all other points at fractions of distance
        # see `contour_labels.py` and `test_contour_labels.py`
        other_points = {}
        for i, label in enumerate(contour):
            other_points[label] = find_point_at_fraction(p1,
                                                         p2,
                                                         p3,
                                                         f=i/(len(contour)-1))

        # Append to data frame
        tmp = pd.DataFrame.from_dict(other_points, orient='index')
        tmp.columns = ['x', 'y', 'z']
        tmp['label'] = tmp.index
        df = df.append(tmp, ignore_index=True, sort=True)

        # Remove duplicates, keeping the first computations
        df = df.drop_duplicates(subset='label', keep='first')

    # Save The positions as files for the three main standard systems
    # ---------------------------------------------------------------
    # First in 3D
    idx = df.label.isin(system1020)
    df_1020 = df.loc[idx, :]
    fname = '../data/standard_1020.tsv'
    df_1020.to_csv(fname, sep='\t', na_rep='n/a', index=False,
                   float_format='%.4f')

    idx = df.label.isin(system1010)
    df_1010 = df.loc[idx, :]
    fname = '../data/standard_1010.tsv'
    df_1010.to_csv(fname, sep='\t', na_rep='n/a', index=False,
                   float_format='%.4f')

    idx = df.label.isin(system1005)
    df_1005 = df.loc[idx, :]
    fname = '../data/standard_1005.tsv'
    df_1005.to_csv(fname, sep='\t', na_rep='n/a', index=False,
                   float_format='%.4f')

    # Now in 2D using stereographic projection
    fnames = ['../data/standard_1020_2D.tsv',
              '../data/standard_1010_2D.tsv',
              '../data/standard_1005_2D.tsv']

    for df, fname in zip([df_1020, df_1010, df_1005], fnames):
        xs, ys = stereographic_projection(df.values[:, 1],
                                          df.values[:, 2],
                                          df.values[:, 3])

        df_2d = pd.DataFrame({'label': df.label.tolist(), 'x': xs, 'y': ys})
        df_2d.to_csv(fname, sep='\t', na_rep='n/a', index=False,
                     float_format='%.4f')

    # Plot for each standard system
    # -----------------------------
    system = input('Which system do you want to plot? (1020/1010/1005/None)\n')
    if system == '1020':
        df = df_1020
    elif system == '1010':
        df = df_1010
    elif system == '1005':
        df = df_1005
    else:
        df = None

    if df is not None:
        # 3D
        fig, ax = plot_spherical_head()

        for idx, row in df.iterrows():
            ax.scatter3D(row.x, row.y, row.z, c='b')
            ax.text(row.x, row.y, row.z, row['label'], fontsize=5)

        ax.set_title('standard_{}'.format(system))

        # 2D
        fig2, ax2 = plot_2d_head()

        xs, ys = stereographic_projection(df.x, df.y, df.z)

        ax2.scatter(xs, ys, marker='.', color='r')

        for lab, x, y in zip(list(df.label), xs, ys):
            ax2.annotate(lab, xy=(x, y), fontsize=5)

        ax2.set_title('standard_{}'.format(system))

        # Show and wait until done
        fig.show()
        fig2.show()
        done = input('\nClick Enter when finished viewing.\n')
