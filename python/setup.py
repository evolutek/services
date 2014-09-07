from setuptools import setup, find_packages

setup(
    name = "services",
    version = "2015",
    packages = find_packages(),
    namespace_packages = ['evolutek'],

    install_requires = open('requirements.pip').read().splitlines(),
    extra_requires = {
        'web': open('requirements_web.pip').read().splitlines(),
    },

    entry_points = {
        'console_scripts': [
            'ax = evolutek.services.ax:main',
            'buzzer = evolutek.services.buzzer:main',
            'config = evolutek.services.config:main',
            'cs_date = evolutek.services.cs_date:main',
            'echo = evolutek.services.echo:main',
            'homologation_pal = evolutek.services.homologation_pal:main',
            'ia_pal = evolutek.services.ia_pal:main',
            'ia_pmi = evolutek.services.ia_pmi:main',
            'leds = evolutek.services.leds:main',
            'robots_monitor = evolutek.services.robots_monitor:main',
            'tracking = evolutek.services.tracking:main',
            'trajman = evolutek.services.trajman:main',
        ],
    },
)
