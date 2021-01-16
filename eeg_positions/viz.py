"""Visualization utilities."""
# Copyright (c) 2018-2021, Stefan Appelhoff
# BSD-3-Clause

import matplotlib.pyplot as plt
import numpy as np

from eeg_positions.utils import _get_coords_on_circle


def _plot_spherical_head():
    """Plot a spherical head model.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The Figure object.
    ax : matplotlib.axes.Axes
        The Axes object.

    """
    # Start new 3D figure
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    # Add labels, scale limits, equal aspect
    ax.set_xlabel("x", fontsize=20)
    ax.set_ylabel("y", fontsize=20)
    ax.set_zlabel("z", fontsize=20)
    ax.set_aspect("auto")
    ax.set_xlim((-1, 1))
    ax.set_ylim((-1, 1))
    ax.set_zlim((-1, 1))

    # No background
    ax.grid(False)
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.xaxis.pane.set_edgecolor("w")
    ax.yaxis.pane.set_edgecolor("w")
    ax.zaxis.pane.set_edgecolor("w")

    # Plot origin
    max_lim = np.max(np.abs([ax.get_xlim3d(), ax.get_ylim3d(), ax.get_zlim3d()]))
    n_pts = 11
    fake_spine = np.linspace(-max_lim * 6, max_lim * 6, n_pts)
    fake_spine_zeros = np.zeros_like(fake_spine)

    ax.plot(fake_spine, fake_spine_zeros, fake_spine_zeros, color="k")
    ax.plot(fake_spine_zeros, fake_spine, fake_spine_zeros, color="k")
    ax.plot(fake_spine_zeros, fake_spine_zeros, fake_spine, color="k")

    # draw spherical head
    resolution = 100j
    u, v = np.mgrid[0 : 2 * np.pi : resolution, 0 : np.pi : resolution]
    x = np.cos(u) * np.sin(v)
    y = np.sin(u) * np.sin(v)
    z = np.cos(v)
    ax.plot_wireframe(x, y, z, color="k", linestyle=":", alpha=0.1)
    ax.plot_surface(x, y, z, color="k", alpha=0.1)
    ax.set_box_aspect((1, 1, 1))

    return fig, ax


def _plot_2d_head(radius_inner_contour=None):
    """Plot a head in 2D.

    Parameters
    ----------
    radius_inner_contour : int | float | None
        If int or float, draw a circle with that radius
        to visualize an inner contour line.
        Defaults to None, not drawing a circle.
        Can instead also be conveniently set to
        ``eeg_positions.config.RADIUS_INNER_CONTOUR``,
        which is the Fpz-T8-Oz-T7 contour line.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The Figure object.
    ax : matplotlib.axes.Axes
        The Axes object.

    """
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.axes.set_aspect("equal")
    plt.xlabel("x")
    plt.ylabel("y")

    head_radius = 1.0
    linewidth = 1.0

    # Draw head shape
    head_shape = plt.Circle(
        (0, 0), head_radius, color="k", fill=False, linewidth=linewidth
    )
    ax.add_artist(head_shape)

    if radius_inner_contour is not None:
        head_shape = plt.Circle(
            (0, 0), radius_inner_contour, color="k", fill=False, linewidth=linewidth / 2
        )
        ax.add_artist(head_shape)

    # Draw nose
    nose_width = 5
    nose_base_l = _get_coords_on_circle(r=head_radius, steps=nose_width)[-1]
    nose_base_r = _get_coords_on_circle(r=head_radius, steps=nose_width)[1]
    nose_tip = 1.1
    plt.plot((nose_base_l[0], 0), (nose_base_l[1], nose_tip), "k", linewidth=linewidth)
    plt.plot((nose_base_r[0], 0), (nose_base_r[1], nose_tip), "k", linewidth=linewidth)

    ax.vlines(x=0, ymin=-1, ymax=1, color="black", linewidth=linewidth / 2)
    ax.hlines(y=0, xmin=-1, xmax=1, color="black", linewidth=linewidth / 2)

    # Adjust limits:
    ax.set_xlim([-head_radius * 1.6, head_radius * 1.6])
    ax.set_ylim([-head_radius * 1.6, head_radius * 1.6])

    return fig, ax
