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
    version = "2021",
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
            'trajman = evolutek.services.trajman:main',
            'match = evolutek.services.match:main',
            'robot = evolutek.services.robot:main',
            'ai = evolutek.services.ai:main',
            # Utils
            'reset = evolutek.utils.service_reset:main',
        ],
    },
)
