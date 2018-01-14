#!/usr/bin/env python3

from cellaserv.proxy import CellaservProxy

side_map = {
    "yellow": -1,
    "green": 1,
}

def get_side(proxy=None):
    if proxy is None:
        # Get a disposable proxy
        proxy = CellaservProxy

    color = proxy.config.get("match", "color")

    return side_map[color]
