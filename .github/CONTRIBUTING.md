# Contributions

Contributions are welcome in the form of feedback and discussion in issues,
or pull requests for changes to the code.

Once the implementation of a piece of functionality is considered to be free of
bugs and properly documented, it can be incorporated into the `main` branch.

To help developing `eeg_positions`,
you will need a few adjustments to your installation as shown below.

## Install the development version

First make a fork of the repository under your `USERNAME` GitHub account.
Then, in your Python environment follow these steps:

```Shell
git clone https://github.com/USERNAME/eeg_positions
cd eeg_positions
git fetch --tags --prune --prune-tags
python -m pip install -e ".[dev]"
pre-commit install
```

You may also clone the repository via ssh, depending on your preferred workflow
(`git clone git@github.com:USERNAME/eeg_positions.git`).

Note that we are working with "pre-commit hooks".
See https://pre-commit.com/ for more information.

## Running tests and coverage

If you have followed the steps to get the development version,
you can run tests as follows.
From the project root, call:

- `pytest` to run tests and coverage
- `pre-commit run -a` to run style checks (Ruff and some additional hooks)

## Building the documentation

The documentation can be built using [Sphinx](https://www.sphinx-doc.org).

The publicly accessible documentation is built and hosted by
[Read the Docs](https://readthedocs.org/).
Credentials for Read the Docs are currently held by:

- [@sappelhoff](https://github.com/sappelhoff/)

## Info about versioning

We follow a [semantic versioning scheme](https://semver.org/).
This is implemented via [hatch-vcs](https://github.com/ofek/hatch-vcs).

## Making a release on GitHub and PyPi

`eeg_positions` is regularly released on
[GitHub](https://github.com/sappelhoff/eeg_positions/releases)
and
[PyPI](https://pypi.org/project/eeg_positions/).

Credentials are currently held by:

- GitHub
  - Admin
    - [@sappelhoff](https://github.com/sappelhoff/)
- PyPi
  - Owner
    - [@sappelhoff](https://github.com/sappelhoff/)

Releasing on GitHub will automatically trigger a release on PyPi via a GitHub Action
(see `.github/workflows/release.yml`).
The release protocol can be briefly described as follows:

1. Activate your Python environment for `eeg_positions`.
1. Make sure all tests pass and the docs are built cleanly.
1. If applicable, append new authors to the author metadata in the `CITATION.cff` file.
1. Update `docs/changes.rst`, renaming the "current" headline to the new
   version
1. Commit the change and git push to origin `main`.
   Include "REL" in your commit message.
1. Then, make an annotated tag, for example for the version `1.2.3`:
   `git tag -a -m "1.2.3" 1.2.3 origin/main`
   (This assumes that you have a git remote configured with the name "origin" and
   pointing to https://github.com/sappelhoff/eeg_positions).
   **NOTE: Make sure you have your `main` branch up to date for this step!**
1. `git push --follow-tags origin`
1. Make a [release on GitHub](https://help.github.com/en/articles/creating-releases),
   using the git tag from the previous step (e.g., `1.2.3`).
   Fill the tag name into the "Release title" field, and fill the "Description" field
   as you see fit.
1. This will trigger a GitHub Action that will build the package and release it to PyPi.

Then the release is done and `main` has to be prepared for development of
the next release:

1. Add a "Current (unreleased)" headline to `docs/changes.rst`.
1. Commit the changes and git push to `main` (or make a pull request).
