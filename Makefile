SERVICES = ax \
           timer \
           date

help::
	@echo To install all services:
	@echo "    $ make install"
	@echo To run them individualy
	@echo "    $ make service-name"

all::
	for service in $(SERVICES); do \
	    $(MAKE) -C $$service; \
	done

install::
	for service in $(SERVICES); do \
	    $(MAKE) -C $$service install; \
	done

$(SERVICES)::
	$(MAKE) -C $@ run
