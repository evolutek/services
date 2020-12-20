#!/usr/bin/env python3

from setuptools import setup, find_packages
from setuptools.command.develop import develop
from subprocess import check_call
import sys

class PostDevelopCommand(develop):
    def run(self):
        check_call("cp -r conf.d /etc/".split())
        develop.run(self)

setup(
    name = "services",
    version = "2020",
    packages = find_packages(),
    namespace_packages = ['evolutek'],

    cmdclass = {
        'develop': PostDevelopCommand
    },

    install_requires = open('requirements.pip').read().splitlines(),

    entry_points = {
        'console_scripts': [
            # Services
            'config = evolutek.services.config:main',
            'actuators = evolutek.services.actuators:main',
            'ax = evolutek.services.ax:main',
            'ai = evolutek.services.ai:main',
            'trajman = evolutek.services.trajman:main',
            'match = evolutek.services.match:main',
            'map = evolutek.services.map:main',
            # Simulation
            'fake_ax = evolutek.simulation.fake_ax:main',
            'fake_trajman = evolutek.simulation.fake_trajman:main',
            'launch_enemies = evolutek.simulation.launch_enemies:main',
            'launch_robot = evolutek.simulation.launch_robot:main',
            'simulator = evolutek.simulation.simulator:main',
            # Utils
            'match_interface = evolutek.utils.match_interface:main',
            'shell = evolutek.utils.shell.shell:evolutek_shell'
        ],
    },
)
