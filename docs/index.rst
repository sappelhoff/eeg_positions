=================================================
Compute and plot standard EEG electrode positions
=================================================

.. toctree::
   :hidden:
   :glob:

   api
   changes
   auto_examples/index


Highlights
==========

- **Compute and plot standard EEG electrode positions using Python**
    - Just ``pip install eeg_positions``
    - Then take a look at the :ref:`examples <docs-examples>`


- **Get pre-computed electrode positions from the repository /data directory**
    - See in `GitHub <https://github.com/sappelhoff/eeg_positions/tree/master/data>`_


- **Look through the well-commented and documented code base to understand what's going on**
    - Start here: :ref:`API documentation <docs-api>`

Introduction
============

When recording electroencephalography (EEG) data, electrodes are usually placed according to an international standard.
The ``10-20``, and by extension the ``10-10`` and ``10-05`` systems are established sets of rules for this case
:footcite:`10-05-article`.

Even when the actual electrode locations have not been empirically measured during the recording,
an approximation  of these positions is important for for plotting topographies or visualizing locations of sensors
with the help of analysis software.

While standard locations are available in many places such as from Robert Oostenveld's blog
:footcite:`10-05-blog`
or directly from electrode cap manufacturers such as
`Easycap <https://www.easycap.de/>`_,
it is seldom specified and documented how these electrode locations are calculated.

The ``eeg_positions`` repository contains code to compute the standard EEG electrode locations
on a spherical head model for the ``10-20``, ``10-10``, and ``10-05`` system.

There are also utility functions to project the 3D locations to 2D space and to plot them.

Details
=======

We compute the EEG electrode positions on a spherical head model.

EEG electrodes are typically placed on a human's scalp,
so the coordinate system we use for the EEG electrode positions is also described with
reference to humans.

We are working in a 3D coordinate system with a *"RAS"* orientation.
That means that *from the perspective of the human that has the electrodes on their scalp*,
the x-axis is pointing to the right hand side (**R**),
the y-axis is pointing to the front (that is, *"anterior"*, **A**), and
the z-axis is pointing upwards (that is, *"superior"*, **S**).

For more information on this, see the documentation in the
`BIDS specification <https://bids-specification.readthedocs.io/en/latest/99-appendices/08-coordinate-systems.html>`_.

The points in space used to properly define the coordinate system are anatomical landmarks:

- The nasion (NAS)
- The left preauricular point (LPA)
- The right preauricular point (RPA)
- The vertex
- The inion

For more information on this, see the MNE-Python glossary under
`fiducial points <https://mne.tools/dev/glossary.html#term-fiducial-point>`_.

In our spherical head model, the anatomical landmarks correspond to the
following positions (``(x, y, z)``) on the unit sphere:

- NAS = ``(0, 1, 0)``
- LPA = ``(-1, 0, 0)``
- RPA = ``(1, 0, 0)``
- Vertex = ``(0, 0, 1)``
- Inion = ``(0, -1, 0)``

(Note that ``eeg_positions`` also allows for some customization in this regard,
as shown in the :ref:`examples <docs-examples>`.)

.. currentmodule:: eeg_positions

Based on these known points, and the known distribution of EEG electrodes in the
``10-20``, ``10-10``, and ``10-05`` systems,
we then use the function :func:`find_point_at_fraction`,
to calculate the remaining points.

Cite
====

If you find this repository useful and want to cite it in your work,
please go to the
`Zenodo record <https://doi.org/10.5281/zenodo.3718568>`_
and obtain the appropriate citation from the *"Cite as"* section there.

Acknowledgements
================

My thanks to:

- Robert Oostenveld for writing his blog post on EEG electrode positions


- Ed Williams for the helpful correspondence and discussions about
  "intermediate points on a great circle" (see also :footcite:`edwilliams`)


- "Nominal Animal" who helped me to figure out the math for
  the ``find_point_at_fraction`` function :footcite:`stackexchange-nominal`

References
==========

.. footbibliography::
