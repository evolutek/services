#!/usr/bin/env python3

from shell_global import cs, get_robot, set_robot

from ax import ax_shell
from config import config_shell
from trajman import trajman_shell

import click
from click_shell import shell
from os import _exit
from sys import argv
from time import sleep

@shell(prompt='evo-shell > ', intro='Shell to control robot')
def evolutek_shell():
    pass

@evolutek_shell.command()
@click.argument('name')
def robot(name):
    if name not in ['pal', 'pmi']:
        click.echo('Unknow robot [%s]' % name)
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
def trajman():
    if get_robot() is None:
        click.echo('No robot selected')
        return

    trajman_shell()

@evolutek_shell.command()
def config():
    config_shell()

if __name__ == '__main__':
    evolutek_shell()
