#!/usr/bin/env python3

from cellaserv.proxy import CellaservProxy

cs = CellaservProxy()

cs("new_event")

cs.test.print_test(0, 2)
