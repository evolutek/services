SERVICE       = config
EXE           = config.py
SYSTEMD_FILES = config.service
PYTHON3       ?= python3

run::
	$(PYTHON3) $(EXE)

include ../common.mk

upload::
	scp $(EXE) root@$(IP_MINI):$(PREFIX)
