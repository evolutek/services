SERVICE       = ax
FILES         = ax.py
SYSTEMD_FILES = systemd/ax.service

PYTHON3       ?= python3

build:: libdxl.so

clean::
	$(MAKE) -C libdxl clean

libdxl.so:
	$(MAKE) -C libdxl

run:: build
	$(PYTHON3) ax.py

include ../install.mk

install_custom:: build
	mkdir -p $(PREFIX)/usr/lib
	$(INSTALL_FILE) libdxl/libdxl.so -t $(PREFIX)/usr/lib/

uninstall_custom::
	rm -f $(PREFIX)/usr/lib/libdxl.so
