#!/bin/bash

export PWD="$(realpath "$(dirname -- "${BASH_SOURCE[0]}")")"
export PYTHON="$PWD/.venv/bin/python"

cd "$PWD"

python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt

cd -

function install {
    cat "systemd/$1" | envsubst > "/etc/systemd/system/$1"
}

install "actuators.service"
install "ai.service"
install "robot.service"
install "trajman.service"
install "reset.service"
