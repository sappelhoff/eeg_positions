=================================================
Compute and plot standard EEG electrode positions
=================================================

.. toctree::
   :hidden:
   :glob:

   api
   changes
   auto_examples/index

This is the ``eeg_positions`` repository.

Have a look at the :ref:`examples <docs-examples>`.

Or at the :ref:`API documentation <docs-api>`.



When recording electroencephalography (EEG) data, electrodes are usually placed
according to an international standard. The `10-20`, and by extension the
`10-10` and `10-05` systems are established sets of rules for this case
[[1]](https://www.biosemi.com/publications/pdf/Oostenveld2001b.pdf). Even when
the actual electrode locations have not been empirically measured during the
recording, an approximation  of these positions is important for for plotting
topographies or visualizing locations of sensors with the help of analysis
software.

While standard locations are available in many places such as from Robert
Oostenveld's [blog](http://robertoostenveld.nl/electrode/) or directly from
electrode cap manufacturers such as [Easycap](https://www.easycap.de/), it is
seldom specified how these electrode locations are calculated.

**This repository contains code to compute the standard EEG electrode locations
in 3D for the `10-20`, `10-10`, or even `10-05` system.** There are also utility
functions to project the 3D locations to 2D space and plot them.

## At a glance

- The electrode locations are computed on a geometrical sphere centered on the
  origin and with radius 1 (arbitrary units).
- The function uses an algorithm to compute positions at fractions along
  contour lines defined by three points: See the `find_point_at_fraction`
  function in the `eeg_positions/utils.py` file.

## How to work with it

- `git clone` the repository (or download as `.zip` and unpack)
- `cd eeg_positions`
- Using your python environment of choice, install the package and its
  dependencies locally using `pip install -e .[dev]`
- Run the tests using `pytest --doctest-modules`
- Calculate and plot electrodes by calling `python eeg_positions/compute.py`
- Check out `config.py` for the order how electrodes are computed
- ... and see `utils.py` for the `find_point_at_fraction` function that is the
  core of the computations.

## References

- [1] Oostenveld, R., & Praamstra, P. (2001). The five percent electrode system
  for high-resolution EEG and ERP measurements. Clinical neurophysiology,
  112(4), 713-719. doi:
  [10.1016/S1388-2457(00)00527-7](https://www.biosemi.com/publications/pdf/Oostenveld2001b.pdf)

## Acknowledgements

My thanks to:

- Robert Oostenveld for writing his [blog post](http://robertoostenveld.nl/electrode/)
  on electrodes
- Ed Williams for the helpful correspondence and discussions about
  "intermediate points on a great circle" (see his
  [aviation formulary](http://www.edwilliams.org/avform.htm#Intermediate))
- "N. Bach" and "Nominal Animal" who helped me to figure out the math for
  the `find_point_at_fraction` function (see this
  [math.stackexchange.com post](https://math.stackexchange.com/questions/2800845/find-intermediate-points-on-small-circle-of-a-sphere/2805204#2805204))


---

# Details

## Coordinate System Conventions

### 3D Axes and Cartesian Coordinate System

- Imagine the x-axis pointing roughly towards the viewer with increasing values
- The y-axis is orthogonal to the x-axis, pointing to the right of the viewer
  with increasing values
- The z-axis is orthogonal to the xy-plane and pointing vertically up with
  increasing values

### Relationship of Coordinate System to a Human Head

For simplicity, we assume a spherical head shape of a human. Roughly speaking,
the x-axis goes from the left ear through the right ear, the y-axis goes
orthogonally to that from the inion through the nasion, and the z-axis goes
orthogonally to that plane through the vertex of the scalp.

We use the following anatomical landmarks to define the boundaries of the
sphere:

## Cartesian Coordinates

- The left preauricular point = `(-1, 0, 0)` ... coincides with T9
- The right preauricular point = `(1, 0, 0)` ... coincides with T10
- The nasion = `(0, 1, 0)` ... coincides with Nz
- The inion = `(0, -1, 0)` ... coincides with Iz
- The vertex = `(0, 0, 1)` ... coincides with Cz

Hence, the equator of the sphere goes through T9, T10, Nz and Iz.

**Note that these are ASSUMPTIONS**. It would be equally valid to assume the
equator going through T7, T8, Fpz, and Oz.
