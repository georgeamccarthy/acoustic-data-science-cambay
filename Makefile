.PHONY: clean data requirements sync_data_to_s3 sync_data_from_s3 format plot analyse all

#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
PROFILE = default
PROJECT_NAME = acoustic-data-science
PYTHON_INTERPRETER = python3

ifeq (,$(shell which conda))
HAS_CONDA=False
else
HAS_CONDA=True
endif

#################################################################################
# COMMANDS                                                                      #
#################################################################################

## Install Python Dependencies
requirements: test_environment
	$(PYTHON_INTERPRETER) -m pip install -U pip setuptools wheel
	$(PYTHON_INTERPRETER) -m pip install -r requirements.txt

remake_logs:
	echo > 'acoustic_data_science/logs.log'

## Combine raw CSV files into raw feather files.
combine: requirements remake_logs
	$(PYTHON_INTERPRETER) acoustic_data_science/processing/combine_csvs.py

## Process raw feather files into data ready for analysis.
process: requirements remake_logs
	$(PYTHON_INTERPRETER) acoustic_data_science/processing/process_data.py
	$(PYTHON_INTERPRETER) acoustic_data_science/processing/ice_coverage.py

## Make Dataset
data: requirements remake_logs process

## Analyse dataset.
analyse: 
	$(PYTHON_INTERPRETER) acoustic_data_science/analysis/transient_durations.py
	$(PYTHON_INTERPRETER) acoustic_data_science/analysis/whole_year_spl.py

## Create all figures.
plot: 
	$(PYTHON_INTERPRETER) acoustic_data_science/plotting/transient_durations.py
	$(PYTHON_INTERPRETER) acoustic_data_science/plotting/whole_year_spl.py
	$(PYTHON_INTERPRETER) acoustic_data_science/plotting/ice_coverage.py


## Build everything from base.
all: data analyse plot

## Delete all compiled Python files
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

format:
	black --line-length 79 --experimental-string-processing acoustic_data_science/**/*.py

## Set up python interpreter environment
create_environment:
ifeq (True,$(HAS_CONDA))
		@echo ">>> Detected conda, creating conda environment."
ifeq (3,$(findstring 3,$(PYTHON_INTERPRETER)))
	conda create --name $(PROJECT_NAME) python=3
else
	conda create --name $(PROJECT_NAME) python=2.7
endif
		@echo ">>> New conda env created. Activate with:\nsource activate $(PROJECT_NAME)"
else
	$(PYTHON_INTERPRETER) -m pip install -q virtualenv virtualenvwrapper
	@echo ">>> Installing virtualenvwrapper if not already installed.\nMake sure the following lines are in shell startup file\n\
	export WORKON_HOME=$$HOME/.virtualenvs\nexport PROJECT_HOME=$$HOME/Devel\nsource /usr/local/bin/virtualenvwrapper.sh\n"
	@bash -c "source `which virtualenvwrapper.sh`;mkvirtualenv $(PROJECT_NAME) --python=$(PYTHON_INTERPRETER)"
	@echo ">>> New virtualenv created. Activate with:\nworkon $(PROJECT_NAME)"
endif

## Test python environment is setup correctly
test_environment:
	$(PYTHON_INTERPRETER) test_environment.py
