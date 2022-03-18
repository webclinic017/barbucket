from pathlib import Path

from barbucket.app.logging_preparator import LoggingPreparator
from barbucket.app.cli import cli


def main():
    """Docstring"""
    _make_dirs()
    lp = LoggingPreparator()
    lp.setup_logging()
    cli()  # Run cli


def _make_dirs() -> None:
    Path.mkdir(Path.home() / ".barbucket/tv_screener",
               parents=True, exist_ok=True)
    Path.mkdir(Path.home() / ".barbucket/config",
               parents=True, exist_ok=True)
    Path.mkdir(Path.home() / ".barbucket/database",
               parents=True, exist_ok=True)
    Path.mkdir(Path.home() / ".barbucket/logs",
               parents=True, exist_ok=True)


if __name__ == "__main__":
    main()
