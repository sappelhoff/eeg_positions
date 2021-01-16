.PHONY: all clean inplace test isort black format flake check-manifest pep build-doc conda

all: clean inplace pep test

inplace:
	python -m pip install --upgrade pip
	python -m pip install --editable ".[test]" --no-cache-dir

clean:
	find . -type d -name 'eeg_positions.egg-info' -exec rm -rf {} +;
	find . -type d -name 'dist' -exec rm -rf {} +;
	find . -type d -name 'build' -exec rm -rf {} +;
	find . -type d -name '__pycache__' -exec rm -rf {} +;
	find . -type d -name '.pytest_cache' -exec rm -rf {} +;
	find . -type f -name 'coverage.xml' -exec rm -rf {} +;
	find . -type f -name '.coverage' -exec rm -rf {} +;

test:
	pytest --doctest-modules --cov=eeg_positions/ --cov-report=xml --cov-config=setup.cfg --verbose -s

isort:
	isort eeg_positions

black:
	black eeg_positions

format: isort black

flake:
	flake8 --docstring-convention numpy .

check-manifest:
	check-manifest .

pep: flake check-manifest

build-doc:
	cd docs; make clean
	cd docs; make html
	cd docs; make view

conda:
	conda env remove -n eegpos
	conda create --yes -n eegpos Python=3.8
