SHELL := /bin/zsh
ROOT := $(shell pwd)
MAPPING := PROJECT_MAPPING.json

.PHONY: accuracy

accuracy:
	@python3 tools/porting/bootstrap.py --mapping $(MAPPING) --cases tools/accuracy/cases.json
