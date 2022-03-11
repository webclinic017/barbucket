from barbucket.util.logging_preparator import LoggingPreparator
from barbucket.util.cli import cli


def main():
    """Docstring"""
    lp = LoggingPreparator()
    lp.setup_logging()
    cli()  # Run cli


if __name__ == "__main__":
    main()
