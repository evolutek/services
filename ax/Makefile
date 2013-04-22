SERVICE       = ax
EXE           = ax.py
SYSTEMD_FILES = systemd/ax.service

PYTHON3       ?= python3

build:: libdxl.so

clean::
	$(MAKE) -C libdxl clean

libdxl.so:
	$(MAKE) -C libdxl

run:: build
	$(PYTHON3) ax.py

include ../common.mk

install:: build
	$(INSTALL_LIB) libdxl/libdxl.so $(PREFIX)/usr/lib/
	$(INSTALL_FILE) udev/100-ax.rules /usr/lib/udev/rules.d

uninstall::
	rm -f $(PREFIX)/usr/lib/libdxl.so
	rm -f /usr/lib/udev/rules.d/100-ax.rules
