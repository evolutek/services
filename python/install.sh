#!/bin/bash

export PYTHON="which python | head -n1"

cat "" | envsubst > /etc/systemd/system/
