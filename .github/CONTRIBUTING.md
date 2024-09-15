# Contributions

Contributions are welcome in the form of feedback and discussion in issues,
or pull requests for changes to the code.

Once the implementation of a piece of functionality is considered to be free of
bugs and properly documented, it can be incorporated into the `main` branch.

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
