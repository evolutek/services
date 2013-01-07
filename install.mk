PREFIX         ?= /opt/evolutek
SYSTEMD_PREFIX ?= /usr/lib/systemd
INSTALL_FILE   = install -m 644 -p -D
INSTALL_EXEC   = install -m 755 -p -D
INSTALL_LIB    = $(INSTALL_EXEC)

install:: install_service_files install_systemd_files install_custom

install_service_files:: $(EXE)
	$(INSTALL_EXEC) $(EXE) $(PREFIX)/usr/lib/cs_services/$(SERVICE)

install_systemd_files:: $(SYSTEMD_FILES)
	$(INSTALL_FILE) $(SYSTEMD_FILES) -t $(SYSTEMD_PREFIX)
	for file in $(SYSTEMD_FILES); do \
	    sed -i 's,$$PREFIX,$(PREFIX),g' $(SYSTEMD_PREFIX)/$$(basename $$file); \
	done

install_custom::

uninstall: uninstall_service_files uninstall_systemd_files uninstall_custom

uninstall_service_files:
	rm -f $(PREFIX)/usr/lib/cs_services/$(SERVICE)

uninstall_systemd_files:
	for file in $(SYSTEMD_FILES); do \
	    rm -f $(SYSTEMD_PREFIX)/$$file; \
	done

uninstall_custom::
