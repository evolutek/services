SERVICE       = ia
EXE           = ia.py
SYSTEMD_FILES = ia.service
PYTHON3       ?= python3

FILES = robot.py homologation_pal.py pathfinding.py objective.py robot_status.py ia.py ip_pmi.py

run::
	$(PYTHON3) ia.py

include ../common.mk

upload::
	scp $(FILES) root@$(HOST_ROBOT):$(PREFIX)
