#!/usr/bin/env python3

from configparser import ConfigParser, NoSectionError

from cellaserv.service import Service

CONFIG_FILE = "config.ini"

class Config(Service):

    def __init__(self):
        super().__init__()

        self.config_file = ConfigParser()
        self.temporary_config = {}

    def setup(self):
        super().setup()

        self.config_file.read([CONFIG_FILE,])

    @Service.action
    def get(self, section:str, option:str) -> str:
        """Return value from config file."""
        if section + '.' + option in self.temporary_config:
            return self.temporary_config[section + '.' + option]

        return self.config_file.get(section, option)

    @Service.action
    def set(self, section:str, option:str, value:str) -> None:
        """Write config value."""

        # Flush temporary value
        if section + '.' + option in self.temporary_config:
            del self.temporary_config[section + '.' + option]

        try:
            self.config_file.set(section, option, value)
        except NoSectionError:
            self.config_file.add_section(section)
            self.config_file.set(section, option, value)

        self.write_config()

    def write_config(self):
        with open(CONFIG_FILE, "w") as f:
            self.config_file.write(f)

    @Service.action
    def set_tmp(self, section:str, option:str, value:str) -> None:
        """Set a temporary value."""
        self.temporary_config[section + '.' + option] = value

    @Service.action
    def write(self) -> None:
        """Write temporary config to file."""
        for key, value in self.temporary_config.items():
            section, option = key.split('.', 1)

            # We can't use self.set() because it modifies self.temporary_config
            try:
                self.config_file.set(section, option, value)
            except NoSectionError:
                self.config_file.add_section(section)
                self.config_file.set(section, option, value)

        self.write_config()
        self.temporary_config.clear()

def main():
    config = Config()
    config.run()

if __name__ == '__main__':
    main()
