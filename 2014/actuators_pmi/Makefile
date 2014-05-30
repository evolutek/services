SERVICE       = actuators_pmi
EXE           = actuators_pmi.py
SYSTEMD_FILES = actuators_pmi.service
PYTHON3       ?= python3

build::

run::
	$(PYTHON3) actuators_pmi.py

upload::
	scp actuators_pmi.py root@$(HOST_ROBOT):$(PREFIX)

include ../../common.mk
