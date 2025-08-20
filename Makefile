SHELL := /bin/zsh
ROOT := $(shell pwd)
MAPPING := PROJECT_MAPPING.json

.PHONY: accuracy lst-one lst-all

accuracy:
	@python3 tools/porting/bootstrap.py --mapping $(MAPPING) --cases tools/accuracy/cases.json

lst-one:
	@if [ -z "$(FILE)" ]; then echo "Usage: make lst-one FILE=path/to/file"; exit 1; fi
	python3 tools/lst/build_lst.py $(FILE) --out tools/lst/out/$(shell basename $(FILE)).lst.json
	python3 tools/lst/verify.py tools/lst/out/$(shell basename $(FILE)).lst.json
	python3 tools/lst/to_md.py tools/lst/out/$(shell basename $(FILE)).lst.json --out tools/lst/out/$(shell basename $(FILE)).md

lst-all:
	python3 tools/lst/run_all.py
	python3 tools/lst/verify.py tools/lst/out/*.lst.json
	python3 tools/lst/to_md_all.py
	python3 tools/lst/index_symbols.py --out tools/lst/out/symbols.index.json
