#!/bin/sh

CMD="cellaquery --verbose"
IP=10.3.90.19
PORT=4242

$CMD camera.start position=1
$CMD camera.set_device ip=$IP port=$PORT
$CMD camera.process
