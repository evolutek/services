#!/bin/bash

export PYTHON="$(which python | head -n1)"

function install {
    cat "systemd/$1" | envsubst > "/etc/systemd/system/$1"
}

install "actuators.service"
install "ai.service"
install "robot.service"
install "trajman.service"
install "reset.service"
