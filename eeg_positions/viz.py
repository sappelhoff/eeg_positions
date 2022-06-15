"""Visualization utilities."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from eeg_positions.config import RADIUS_INNER_CONTOUR
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


def _plot_2d_head(radius_inner_contour=None, show_axis=False):
    """Plot a head in 2D.

    Parameters
    ----------
    radius_inner_contour : int | float | None
        If int or float, draw a circle with that radius to visualize an inner
        contour line. Defaults to None, not drawing a circle. Can instead also
        be conveniently set to ``eeg_positions.config.RADIUS_INNER_CONTOUR``,
        which is the Fpz-T8-Oz-T7 contour line.
    show_axis : bool
        Whether or not to show the coordinate system x- and y-axes. Defaults to False.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The Figure object.
    ax : matplotlib.axes.Axes
        The Axes object.

    """
    fig, ax = plt.subplots()
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
    ax.plot((nose_base_l[0], 0), (nose_base_l[1], nose_tip), "k", linewidth=linewidth)
    ax.plot((nose_base_r[0], 0), (nose_base_r[1], nose_tip), "k", linewidth=linewidth)

    ax.vlines(
        x=0,
        ymin=-1,
        ymax=1,
        color="black",
        linewidth=linewidth / 2,
        linestyles="dotted",
    )
    ax.hlines(
        y=0,
        xmin=-1,
        xmax=1,
        color="black",
        linewidth=linewidth / 2,
        linestyles="dotted",
    )

    # Adjust limits
    ax.set_xlim([-head_radius * 1.1, head_radius * 1.1])
    ax.set_ylim([-head_radius * 1.1, head_radius * 1.1])

    fig.set_tight_layout(True)
    if not show_axis:
        ax.set_axis_off()

    return fig, ax


def plot_coords(coords, scatter_kwargs={}, text_kwargs={}):
    """Plot standard EEG electrode coordinates.

    Parameters
    ----------
    coords : pandas.DataFrame
        The standard EEG electrode coordinates as computed on a sphere.
        A pandas DataFrame object with the columns ``"label"``, ``"x"``,
        ``"y"``, and optionally ``"z"``.
    scatter_kwargs : dict
        Optional keyword arguments to be passed to the
        :meth:`matplotlib.axes.Axes.scatter`
        or its 3D variant, depending on the dimensions of `coords`.
    text_kwargs : dict
        Optional keyword arguments to be passed to the
        :meth:`matplotlib.axes.Axes.text`.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The Figure object.
    ax : matplotlib.axes.Axes
        The Axes object.

    """
    # input check
    if not isinstance(coords, pd.DataFrame):
        raise ValueError("`coords` must be a pandas DataFrame object.")
    else:
        for colname in ["label", "x", "y"]:
            if colname not in coords.columns:
                raise ValueError(f"`coords` does not have a required column {colname}.")

    # What kind of plot to prepare
    dim = "3d" if "z" in coords.columns else "2d"

    # update kwargs
    scatter_settings = dict()
    scatter_settings.update(scatter_kwargs)
    text_settings = dict(fontsize=6)
    text_settings.update(text_kwargs)

    if dim == "2d":
        fig, ax = _plot_2d_head(RADIUS_INNER_CONTOUR)
        ax.scatter(coords["x"], coords["y"], zorder=2.5, **scatter_settings)
        for _, row in coords.iterrows():
            ax.text(row["x"], row["y"], row["label"], **text_settings)

    else:
        assert dim == "3d"
        fig, ax = _plot_spherical_head()

        for _, row in coords.iterrows():
            ax.scatter3D(row["x"], row["y"], row["z"], **scatter_settings)
            ax.text(row["x"], row["y"], row["z"], row["label"], **text_settings)

    return fig, ax
