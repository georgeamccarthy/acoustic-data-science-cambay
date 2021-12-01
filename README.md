Acoustic Data Science
==============================

Exploring sea ice processes in the Arctic with acoustic physics and data science.

## Usage
---
- Place the raw feathers (such as `2018_08.feather`, `2018_09.feather` and so on) in `/data/raw/raw_feathers`.
- Run `make all`.

Everything will be handled by the pipline.

Note: the raw feathers are not tracked by this repo and are not yet available for download.

## Requirements
---
- Python 3.8+
- Run `make test_environment` to check if you are set up correctly.
- See requirements.txt for required packages.
- Also see `Makefile` for any external requirements including `Make`.
