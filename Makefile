SERVICES = ax \
	   buzzer \
	   date \
	   pmi \
	   timer \
	   tweet

help::
	@echo To install all services:
	@echo "    $ make install"
	@echo To run them individualy
	@echo "    $ make service-name"

every_services::
	for service in $(SERVICES); do \
	    $(MAKE) -C $$service $(COMMAND); \
	done

all:: every_services

install:: COMMAND=install
install:: every_services

uninstall:: COMMAND=uninstall
uninstall:: every_services

clean:: COMMAND=clean
clean:: every_services

$(SERVICES)::
	$(MAKE) -C $@ run
