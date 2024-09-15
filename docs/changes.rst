:orphan:

=========
Changelog
=========

2.1.1 (2024-09-15)
------------------
- update packaging infrastructure to use `pyproject.toml`, by `Stefan Appelhoff`_ (:github:`#21`)
- change build backend from setuptools to hatching and hatch-vcs, by `Stefan Appelhoff`_ (:github:`#21`)
- change license from BSD-3-Clause to MIT, by `Stefan Appelhoff`_ (:github:`#21`)
- move tests to root directory, pulling them out of the package, by `Stefan Appelhoff`_ (:github:`#21`)
- fix an issue where A1 and A2 electrode positions could be NaN, by `Stefan Appelhoff`_ (:github:`#21`)

2.1.0 (2022-06-15)
------------------
- Add a ``show_axis`` parameter to :func:`eeg_positions.plot_coords`, by `Clemens Brunner`_ (:github:`#7`)
- Add a ``sort`` parameter to :func:`eeg_positions.get_elec_coords`, by `Clemens Brunner`_ (:github:`#12`)
- Allow passing a list of colors to :func:`eeg_positions.plot_coords`, by `Clemens Brunner`_ (:github:`#12`)
- General maintenance and code review, by `Stefan Appelhoff`_

2.0.0 (2021-02-13)
------------------
- documentation pages are available, by `Stefan Appelhoff`_
- ``eeg_positions`` is a package on `PyPI <https://pypi.org/project/eeg-positions/>`_, by `Stefan Appelhoff`_
- a consistent API is available and documented, by `Stefan Appelhoff`_
- several modules have been renamed and restructured, by `Stefan Appelhoff`_
- users have a choice of where to place the equator of the sphere, by `Stefan Appelhoff`_
- ``eeg_positions`` now has an in-built (optional) integration with MNE-Python, by `Stefan Appelhoff`_
- test suite is now run through the GitHub actions continuous integration service, by `Stefan Appelhoff`_
- alias locations that are not part of the 5% system are now available (e.g., M1, A1), by `Stefan Appelhoff`_

1.0.0 (2020-03-19)
------------------
- first git tagged release, by `Stefan Appelhoff`_

0.0.0 (2018-06-05)
------------------
- initial commit to the repository, by `Stefan Appelhoff`_

.. include:: authors.rst
