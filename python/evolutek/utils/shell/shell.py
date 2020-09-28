#!/usr/bin/env python3

from evolutek.utils.shell.shell_global import cs, get_robot, set_robot
from evolutek.utils.shell.ax import ax_shell
from evolutek.utils.shell.config import config_shell
from evolutek.utils.shell.robot import robot_shell
from evolutek.utils.shell.actuators import actuators_shell
from evolutek.utils.shell.mdb import mdb_shell

from evolutek.utils.odom_tools import compute_all

import click
from click_shell import shell
from os import _exit
from sys import argv
from time import sleep

def get_prompt():
    return "evo-shell [%s] > " % get_robot()

@shell(prompt=get_prompt, intro='Shell to control robot')
def evolutek_shell():
    pass

@evolutek_shell.command()
@click.argument('name')
def select_robot(name):
    if name not in ['pal', 'pmi']:
        click.echo('Unknown robot [%s]' % name)
        click.echo('Available robots: [pal, pmi]')
        return

    click.echo('Selection [%s] robot' % name)
    set_robot(name)

@evolutek_shell.command()
def ax():
    if get_robot() is None:
        click.echo('No robot selected')
        return

    ax_shell()

@evolutek_shell.command()
def config():
    config_shell()

@evolutek_shell.command()
def robot():
    if get_robot() is None:
        click.echo('No robot selected')
        return

    robot_shell()

@evolutek_shell.command()
def mdb():
    if get_robot() is None:
        click.echo('No robot selected')
        return

    mdb_shell()

@evolutek_shell.command()
def actuators():
    if get_robot() is None:
        click.echo('No robot selected')
        return

    actuators_shell()

@evolutek_shell.command()
@click.option('-g', '--gains/-no-gains', default=False, help='Compute gains')
@click.option('-d', '--diams/-no-diams', default=False, help='Compute diameters')
@click.option('-s', '--space/-no-space', default=False, help='Compute spacing')
@click.option('-a', '--all/-no-all', default=False, help='Compute all')
@click.option('-c', '--config/-no-config', default=False, help='Set in the config the new values')
def odom(gains, diams, space, all, config):
    if get_robot() is None:
        click.echo('No robot selected')
        return

    compute_all(gains, diams, space, all, config, get_robot())

if __name__ == '__main__':
    evolutek_shell()
