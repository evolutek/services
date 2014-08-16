SERVICES = \
	   ax \
	   battery_monitor \
	   buzzer \
	   leds \
	   mbed \
	   robot \
	   tirette \
	   tracking \
	   trajman

help::
	@echo == How to use this Makefile ==
	@echo Install all services to the local system:
	@echo "    $ make install"
	@echo Run one service individualy:
	@echo "    $ make service-name"
	@echo Upload all services to the robot:
	@echo "    $ make upload"

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

upload:: COMMAND=upload
upload:: every_services

$(SERVICES)::
	$(MAKE) -C $@ run
