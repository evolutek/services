#!/bin/sh

CMD="cellaquery --verbose"
IP=192.168.3.192
PORT=4242

$CMD camera.start position=1
$CMD camera.set_device ip=$IP port=$PORT
$CMD camera.process
