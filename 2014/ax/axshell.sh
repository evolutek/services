#!/bin/bash

ax_id=

function prompt {
    echo -en "\e[34;1max => \e[32m$ax_id\e[34m : \e[0m"
}

function execute {
    case $1 in
        id)
            ax_id=$2
            ;;
        get)
            cellaservctl r ax/$ax_id get_present_position
            ;;
        move)
            cellaservctl r ax/$ax_id mode_joint
            cellaservctl r ax/$ax_id move goal=$2
            ;;
        wheel)
            cellaservctl r ax/$ax_id mode_wheel
            if [ $2 -lt 0 ]; then
                cellaservctl r ax/$ax_id side=-1 speed=$((- $2))
            else
                cellaservctl r ax/$ax_id side=1 speed=$2
            fi
            ;;
        stop)
            ;;
        exit)
            exit 1
            ;;
        *)
            echo "list of commands:"
            echo " - id <id>           set the id of the ax to change"
            echo " - get               get the current position of the ax"
            echo " - move <position>   move in joint mode to position"
            echo " - wheel <speed>     move in wheel mode with spped +-"
            echo " - stop              stop everything"
            echo " - exit              exit the soft"
            ;;

    esac
}

echo -n "set ax id to use : "
read ax_id

prompt
while read cmd; do
    execute $cmd
    prompt
done
