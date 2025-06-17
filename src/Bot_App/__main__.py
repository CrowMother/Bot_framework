import logging
from . import util


def main():
    """Entry point for running the package as a script."""
    util.setup_logging(level=logging.INFO)


if __name__ == "__main__":
    main()

