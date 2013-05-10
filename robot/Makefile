SERVICE       = ia
EXE           = ia.py
SYSTEMD_FILES = ia.service
PYTHON3       ?= python3

run::
	$(PYTHON3) ia.py

include ../common.mk

upload::
	scp robot.py root@$(IP_MINI):$(PREFIX)
