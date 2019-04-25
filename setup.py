"""Setup eeg_positions."""
from setuptools import setup, find_packages
from os import path
import io

here = path.abspath(path.dirname(__file__))

# Get long description from README file
with io.open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='eeg_positions',
      version='0.1.1',
      description=('Functions and data to compute and plot standard EEG'
                   ' electrode positions.'),
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='http://github.com/sappelhoff/eeg_positions',
      author='Stefan Appelhoff',
      author_email='stefan.appelhoff@mailbox.org',
      license='BSD-3-Clause',
      classifiers=[
        'Topic :: Scientific/Engineering :: Mathematics',
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Science/Research'
      ],
      keywords='EEG electrodes standard positions 1020 1010 1005 percent',
      packages=find_packages(),
      install_requires=['numpy>=1.14.2', 'matplotlib>=2.0.2',
                        'pandas>=0.23.0'],
      python_requires='>=3',
      extras_require={
        'test': ['pytest']
      },
      project_urls={
        'Bug Reports': 'https://github.com/sappelhoff/eeg_positions/issues',
        'Source': 'https://github.com/sappelhoff/eeg_positions'})
