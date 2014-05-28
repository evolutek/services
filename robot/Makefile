SERVICE       = ia
EXE           = ia.py
SYSTEMD_FILES = ia.service
PYTHON3       ?= python3

run::
	$(PYTHON3) ia.py

include ../common.mk

upload::
	scp robot.py root@$(HOST_ROBOT):$(PREFIX)
	scp homologation_pal.py root@$(HOST_ROBOT):$(PREFIX)
	scp pathfinding.py root@$(HOST_ROBOT):$(PREFIX)
	scp objective.py root@$(HOST_ROBOT):$(PREFIX)
	scp robot_status.py root@$(HOST_ROBOT):$(PREFIX)
