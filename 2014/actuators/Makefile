SERVICE       = actuators
EXE           = actuators.py
SYSTEMD_FILES = actuators.service
PYTHON3       ?= python3

build::

run::
	$(PYTHON3) actuators.py

upload::
	scp actuators.py root@$(HOST_ROBOT):$(PREFIX)

include ../../common.mk
