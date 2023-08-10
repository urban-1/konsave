.PHONY: help all setup dev-setup check clean distclean maintclean pyfmt black usort tests

all: setup

help:
		@echo "konsave helper:"
		@echo ""
		@echo " - setup:        User-level setup"
		@echo " - dev-setup:    Development setup"
		@echo " - checks:       Format the code with pyfmt and lint"
		@echo " - clean:        Remove all pyc files"
		@echo " - distclean:    Remove any eggs/builds"
		@echo " - maintclean:   Remove virtual env and dist files"
		@echo ""

setup:
		@echo "Setting Up (user)"
		@python3 -m venv .venv
		@(. .venv/bin/activate && \
				pip install -r requirements.txt && \
				python -m pip install --upgrade pip \
		)

dev-setup: setup
		@echo "Setting Up (dev)"
		@@(. .venv/bin/activate && pip install -r requirements_dev.txt)


checks: black pylint

black:
		@echo " * Running black"
		@black --safe konsave

pylint:
		@echo " * Running pylint"
		@pylint konsave

clean:
		@find . -name "*.pyc" -exec rm -f {} \;
		@find . -name '__pycache__' -type d | xargs rm -fr

distclean: clean
		rm -fr *.egg *.egg-info/ .eggs/ dist/ build/

maintclean: distclean
		rm -fr .venv/

# TODO: Consider adding proper type-checking
# typecheck:
#		 mypy -p konsave --strict --no-strict-optional --ignore-missing-imports --install-types
#		 mypy -p tests --no-strict-optional --ignore-missing-imports --install-types

tests:
		python3 ./test.py


release-test: distclean
	python setup.py sdist bdist_wheel
	twine upload -r testpypi dist/*

release: distclean
	python setup.py sdist bdist_wheel
	twine upload dist/*