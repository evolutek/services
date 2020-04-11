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
    extra_requires = {
        'web': open('requirements_web.pip').read().splitlines(),
    },

    entry_points = {
        'console_scripts': [
            'config = evolutek.services.config:main',
            'actuators = evolutek.services.actuators:main',
            'fake_ax = evolutek.simulation.fake_ax:main',
            'fake_trajman = evolutek.simulation.fake_trajman:main'
        ],
    },
)
