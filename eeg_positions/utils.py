"""Functions to calculate and plot standard EEG electrode position systems."""
# Copyright (c) 2018, Stefan Appelhoff
# BSD-3-Clause

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa


def find_point_at_fraction(p1, p2, p3, f):
    """Find a point on an arc spanned by three points.

    Given three points `p1`, `p2` and `p3` on a sphere with origin (0, 0, 0),
    find the coordinates of a point `p` at a fraction `f` of the overall
    distance on an arc spanning from `p1` over `p2` to `p3`. Given this
    assumption, for fractions of zero, `p` will equal `p1`; for fractions of
    one, `p` will equal `p3`; and for fractions of one half, `p` will equal
    `p2` [1].

    Parameters
    ----------
    p1, p2, p3 : tuple
        Each tuple containing x, y, z cartesian coordinates.

    f : float
        Fraction of distance from `p1` to `p3` over p2` at which
        to find coordinates of `p`.

    Returns
    -------
    p : tuple
     Containing x, y, z cartesian coordinates.

    Notes
    -----
    The assumptions of this function require `p1`, `p2` and `p3` to be
    equidistant from the origin. They must not be collinear (i.e., all be
    along one line) and none of the points may be equal.

    References
    ----------
    .. [1] Nominal Animal
       (https://math.stackexchange.com/users/318422/nominal-animal),
       find intermediate points on small circle of a sphere,
       URL (version: 2018-06-02): https://math.stackexchange.com/q/2805204

    Examples
    --------
    >>> find_point_at_fraction((1., 0., 0.), (0., 0., 1.), (-1., 0., 0.), f=0.)
    (1., 0., 0.)
    >>> find_point_at_fraction((1., 0., 0.), (0., 0., 1.), (-1., 0., 0.), f=.5)
    (0., 0., 1.)
    >>> find_point_at_fraction((1., 0., 0.), (0., 0., 1.), (-1., 0., 0.), f=1.)
    (-1., 0., 0.)
    >>> find_point_at_fraction((1., 0., 0.), (0., 0., 1.), (-1., 0., 0.), f=.3)
    (0.5878, 0.0, 0.809)

    """
    # Unpack the point tuples
    x1, y1, z1 = p1
    x2, y2, z2 = p2
    x3, y3, z3 = p3

    # Using the cross product, find unit normal vector (xn, yn, zn)
    # of the plane spanning the three points:
    x12 = x2 - x1
    y12 = y2 - y1
    z12 = z2 - z1
    x13 = x3 - x1
    y13 = y3 - y1
    z13 = z3 - z1

    xn = y12*z13 - z12*y13
    yn = z12*x13 - x12*z13
    zn = x12*y13 - y12*x13

    n = np.sqrt(xn**2 + yn**2 + zn**2)

    if n <= 0.:
        raise ValueError('Points are either collinear '
                         'or share the same coordinates.')

    xn = xn/n
    yn = yn/n
    zn = zn/n

    # Use dot product to get signed distance from plane to origin
    # interchangeably use p1, p2, or p3 with normal vector
    d = xn*x1 + yn*y1 + zn*z1

    # At intersection of sphere and plane, we have a circle
    # with the following center:
    xc = d*xn
    yc = d*yn
    zc = d*zn

    # Construct a 2D coordinate system with the unit circle corresponding
    # to the above circle with first axis towards p1 and second towards p2:
    # 2D U axis unit vector
    xu = x1 - xc
    yu = y1 - yc
    zu = z1 - zc

    # 2D V axis unit vector
    xv = yn*zu - zn*yu
    yv = zn*xu - xn*zu
    zv = xn*yu - yn*xu

    # Choose V axis towards (x2, y2, z2)
    v2 = (x2 - xc)*xv + (y2 - yc)*yv + (z2 - zc)*zv
    if v2 < 0.:
        xv = -xv
        yv = -yv
        zv = -zv

    # Find theta, the positive plane angle towards p3 (x3, y3, z3).
    xt = x3 - xc
    yt = y3 - yc
    zt = z3 - zc

    thetau = xt*xu + yt*yu + zt*zu
    thetav = xt*xv + yt*yv + zt*zv
    theta = np.arctan2(thetav, thetau)

    if theta < 0.:
        # Add 360 degrees, or 2*Pi in radians, to make it positive
        theta = theta + 2*np.pi

    # Now calculate coordinates at fraction
    x = xc + xu * np.cos(f*theta) + xv*np.sin(f*theta)
    y = yc + yu * np.cos(f*theta) + yv*np.sin(f*theta)
    z = zc + zu * np.cos(f*theta) + zv*np.sin(f*theta)

    # Round to 4 decimals and collect the points in tuple
    p = np.asarray((x, y, z))
    p = tuple(p.round(decimals=4))
    return p


# Convenient helper function to access xyz coordinates from df
def get_xyz(df, label):
    """Get xyz coordinates from a pandas data frame.

    Parameters
    ----------
    df : DataFrame
        Data frame with (at least) columns x, y, z, label

    label : string
        Electrode label for which to get x, y, z

    Returns
    -------
    x, y, z : float
        x, y, z 3D positions of electrodes on a unit sphere

    """
    # Check that all labels are present
    for var in ['label', 'x', 'y', 'z']:
        if var not in df.columns:
            raise ValueError('df must contain a column "{}"'.format(var))

    # Check we get exactly one row of data
    subdf = df[df['label'] == label]
    nrows = subdf.shape[0]
    if nrows == 0 or nrows > 1:
        raise ValueError('Expected one row of data but got {}'.format(nrows))

    # Get the data
    x = float(df[df['label'] == label].x)
    y = float(df[df['label'] == label].y)
    z = float(df[df['label'] == label].z)
    return x, y, z


def plot_spherical_head():
    """Plot a spherical head model.

    Returns
    -------
    fig, ax : figure and axes objects

    """
    # Start new 3D figure
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Add labels, scale limits, equal aspect
    ax.set_xlabel('x', fontsize=20)
    ax.set_ylabel('y', fontsize=20)
    ax.set_zlabel('z', fontsize=20)
    ax.set_aspect('equal')
    ax.set_xlim((-1, 1))
    ax.set_ylim((-1, 1))
    ax.set_zlim((-1, 1))

    # No background
    ax.grid(False)
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.xaxis.pane.set_edgecolor('w')
    ax.yaxis.pane.set_edgecolor('w')
    ax.zaxis.pane.set_edgecolor('w')

    # Plot origin
    max_lim = np.max(np.abs([ax.get_xlim3d(),
                             ax.get_ylim3d(),
                             ax.get_zlim3d()]))
    n_pts = 11
    fake_spine = np.linspace(-max_lim*6, max_lim*6, n_pts)
    fake_spine_zeros = np.zeros_like(fake_spine)

    ax.plot(fake_spine, fake_spine_zeros, fake_spine_zeros, color='k')
    ax.plot(fake_spine_zeros, fake_spine, fake_spine_zeros, color='k')
    ax.plot(fake_spine_zeros, fake_spine_zeros, fake_spine, color='k')

    # draw spherical head
    resolution = 100j
    u, v = np.mgrid[0:2*np.pi:resolution, 0:np.pi:resolution]
    x = np.cos(u)*np.sin(v)
    y = np.sin(u)*np.sin(v)
    z = np.cos(v)
    ax.plot_wireframe(x, y, z, color='k', linestyle=':', alpha=0.1)

    return fig, ax


def _get_coords_on_circle(cx=0, cy=0, r=1, steps=180/20):
    """Get the cartesian coordinates [x,y] for a number of points on a circle.

    Assume that top of circle is 0 degrees

    Parameters
    ----------
    cx : int
        x coordinate of origin of circle, default: 0
    cy : int
        y coordinate of origin of circle, default: 0
    r : int
        radius of circle, default: 1
    steps : int
        spacing between evenly spaced points on the
        circle in degrees, default: 9 (360 degrees
        divided into 40 parts, i.e., 5 percent parts)


    Returns
    -------
    coords : list
        nested list of [[x1,y1], [x2,y2], ...]

    """
    # Make sure we are dealing with integer steps
    assert steps/int(steps) == 1.0
    steps = int(steps)

    coords = []
    for a in np.arange(0, 360, steps):
        x = cx + r * np.cos(np.deg2rad(a))
        y = cy + r * np.sin(np.deg2rad(a))
        coords.append([x, y])

    # Exchange x and y so that 0 degree is top of circle
    # also round off
    coords = [[round(y, 5), round(x, 5)] for x, y in coords]  # noqa

    return coords


def stereographic_projection(x, y, z, scale=1.):
    """Calculate the stereographic projection.

    Given a unit sphere with radius ``r = 1`` and center at
    The origin. Project the point ``p = (x, y, z)`` from the
    sphere's South pole (0, 0, -1) on a plane on the sphere's
    North pole (0, 0, 1).

    P' = P * (2r / (r + z))

    Parameters
    ----------
    x, y, z : float
        x, y, z 3D positions of electrodes on a unit sphere

    scale : scale to change the projection point. Defaults
            to one, which is on the sphere.


    Returns
    -------
    x, y : float
        x, y 2D positions of electrodes as projected onto a unit circle

    """
    mu = 1. / (scale + z)
    x = x*mu
    y = y*mu
    return np.asarray(x), np.asarray(y)


def plot_2d_head():
    """Plot a head in 2D.

    Returns
    -------
    fig, ax : figure and axes objects

    """
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.axes.set_aspect('equal')
    plt.xlabel('x')
    plt.ylabel('y')

    head_radius = 1.

    # Draw head shape
    head_shape = plt.Circle((0, 0), head_radius,
                            color='k', fill=False, linewidth=2)
    ax.add_artist(head_shape)

    # Draw nose
    nose_width = 5
    nose_base_l = _get_coords_on_circle(r=head_radius, steps=nose_width)[-1]
    nose_base_r = _get_coords_on_circle(r=head_radius, steps=nose_width)[1]
    nose_tip = 1.1
    plt.plot((nose_base_l[0], 0), (nose_base_l[1], nose_tip), 'k', linewidth=2)
    plt.plot((nose_base_r[0], 0), (nose_base_r[1], nose_tip), 'k', linewidth=2)

    # Adjust limits:
    ax.set_xlim([-head_radius*1.6, head_radius*1.6])
    ax.set_ylim([-head_radius*1.6, head_radius*1.6])

    return fig, ax


if __name__ == '__main__':
    pass
