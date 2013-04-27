SERVICE       = tracking
EXE           = tracking.py
SYSTEMD_FILES = tracking.service
PYTHON3       ?= python3

run::
	./setup.sh
	$(PYTHON3) tracking.py

include ../common.mk
