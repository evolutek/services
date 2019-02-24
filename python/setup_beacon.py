from setuptools import setup, find_packages
from setuptools.command.develop import develop
from subprocess import check_call

class PostDevelopCommand(develop):
    def run(self):
        check_call("cp -r evolutek/ /usr/lib/python3.5/site-packages/".split())
        check_call("cp -r conf.d /etc/".split())
        develop.run(self)

setup(
    name = "services",
    version = "2019",
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
            'map = evolutek.services.map:main',
            'match = evolutek.services.match:main',
        ],
    },
)
