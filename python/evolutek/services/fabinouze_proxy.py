#!/usr/bin/env python3

from cellaserv.proxy import CellaservProxy

cs = CellaservProxy()

cs.test.print_test(10, 20)
