from setuptools import setup, find_packages

setup(
    name = "services",
    version = "2018",
    packages = find_packages(),
    namespace_packages = ['evolutek'],

    install_requires = open('requirements.pip').read().splitlines(),
    extra_requires = {
        'web': open('requirements_web.pip').read().splitlines(),
    },

    entry_points = {
        'console_scripts': [
            'ax = evolutek.services.ax:main',
            'config = evolutek.services.config:main',
            'trajman = evolutek.services.trajman:main',
            'actuators = evolutek.services.actuators:main',
            'tirette = evolutek.services.tirette:main',
            'gbts = evolutek.services.gbts:main',
            'gpios = evolutek.services.gpios:main',
        ],
    },
)
