.PHONY: all clean inplace test isort black format flake check-manifest pep build-doc conda

all: clean inplace pep test build-doc

inplace:
	python -m pip install --upgrade pip
	python -m pip install --editable ".[dev]" --no-cache-dir

clean:
	find . -type d -name 'eeg_positions.egg-info' -exec rm -rf {} +;
	find . -type d -name 'dist' -exec rm -rf {} +;
	find . -type d -name 'build' -exec rm -rf {} +;
	find . -type d -name '__pycache__' -exec rm -rf {} +;
	find . -type d -name '.pytest_cache' -exec rm -rf {} +;
	find . -type f -name 'coverage.xml' -exec rm -rf {} +;
	find . -type f -name '.coverage' -exec rm -rf {} +;

test:
	pytest --doctest-modules --doctest-ignore-import-errors --cov=eeg_positions/ --cov-report=xml --cov-config=setup.cfg --verbose -s

isort:
	isort eeg_positions
	isort examples
	isort docs/conf.py

black:
	black eeg_positions
	black examples
	black docs/conf.py

format: isort black

flake:
	flake8 --docstring-convention numpy eeg_positions
	flake8 --docstring-convention numpy examples

check-manifest:
	check-manifest .

pep: flake check-manifest

build-doc:
	rm -rf docs/auto_examples
	rm -rf docs/generated
	cd docs; make clean
	cd docs; make html
	cd docs; make view

conda:
	conda env remove -n eegpos
	conda create --yes -n eegpos Python=3.8
