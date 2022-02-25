from pathlib import Path

from barbucket.config_reader import ConfigReader


def build() -> ConfigReader:
    filepath = Path.home() / ".barbucket/config.cfg"
    return ConfigReader(filepath=filepath)
