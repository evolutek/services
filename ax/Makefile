SERVICE       = ax
EXE           = ax.py
SYSTEMD_FILES = systemd/ax.service

PYTHON3       ?= python3

run::
	$(PYTHON3) ax.py

include ../common.mk

install::
	$(INSTALL_FILE) udev/100-ax.rules /usr/lib/udev/rules.d

uninstall::
	rm -f /usr/lib/udev/rules.d/100-ax.rules
