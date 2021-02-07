:orphan:

.. _docs-api:

=================
API Documentation
=================

All functions described here can be imported from the :py:mod:`eeg_positions` package.

.. automodule:: eeg_positions
   :no-members:
   :no-inherited-members:

.. currentmodule:: eeg_positions

The :func:`find_point_at_fraction` function contains the key algorithm for computing the
standard EEG electode positions on a sphere.
You will most likely not need to use this function in your code directly,
but it is still made availble over the API and the documentation for its key role in the code.

.. autosummary::
   :toctree: generated/

   find_point_at_fraction

The practically most useful functions are listed below.
These will help you to get the electrode positions you need in a usable format

.. autosummary::
   :toctree: generated/

   get_elec_coords
   get_available_elec_names
   get_alias_mapping

Finally, the :py:mod:`eeg_positions` package also exposes a convenient function for
visualizing electrode positons.

.. autosummary::
   :toctree: generated/

   plot_coords
