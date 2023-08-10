"""Konsave entry point."""

import argparse
import logging
from konsave.funcs import (
    config_check,
    install_config,
    list_profiles,
    reset_config,
    save_profile,
    remove_profile,
    apply_profile,
    export,
    import_profile,
    wipe,
)
from konsave.consts import (
    KDE_RELOAD_CMD,
    VERSION,
)

logging.basicConfig(format="%(name)s: %(message)s", level=logging.INFO)


def parse_args() -> argparse.ArgumentParser:
    """
    Parses and returns all arguments
    """
    parser = argparse.ArgumentParser(
        prog="Konsave",
        epilog="Please report bugs at https://www.github.com/urban-1/konsave",
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", help="Enable debug logging"
    )

    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list")

    save_parser = sub.add_parser("save")
    save_parser.add_argument("-f", "--force", action="store_true")
    save_parser.add_argument("name")

    rm_parser = sub.add_parser("remove")
    rm_parser.add_argument("name")

    apply_parser = sub.add_parser("apply")
    apply_parser.add_argument("name")
    apply_parser.add_argument(
        "-r",
        "--reload-kde",
        action="store_true",
        help=f"If set, it will execute the KDE_RELOAD_CMD: '{KDE_RELOAD_CMD}'",
    )

    export_parser = sub.add_parser(
        "export", help="Export a profile to a konsave archive"
    )
    export_parser.add_argument("name")
    export_parser.add_argument("-f", "--force", action="store_true")
    export_parser.add_argument(
        "-o",
        "--output",
        required=False,
        help="Specify the full export path. Any extension will be ignored",
        metavar="<path>",
    )

    import_parser = sub.add_parser(
        "import", help="Import a profile from a konsave archive"
    )
    import_parser.add_argument("path")
    import_parser.add_argument(
        "-n", "--import-name", help="Specify the name of the profile when importing it"
    )

    sub.add_parser("wipe", help="Wipe all profiles - this cannot be undone!")
    sub.add_parser("version", help="Show Konsave version")
    sub.add_parser(
        "reset-config",
        help=(
            "Reset the konsave config to the factory default. This option is "
            "mainly useful for development"
        ),
    )

    sub.add_parser(
        "config-check",
        help=(
            "Check currect config against ~/.config folders/files and show what "
            "is backed up and what is not"
        ),
    )

    return parser.parse_args()


def main():
    """The main function that handles all the arguments and options."""

    # Never force by default
    install_config(force=False)

    args = parse_args()
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(levelname).1s%(asctime)s.%(msecs)03d [%(name)s]: %(message)s",
            datefmt="%d%m %H:%M:%S",
        )
        for handler in logging.getLogger().handlers:
            handler.setFormatter(formatter)

    funcs = {
        "list": list_profiles,
        "save": save_profile,
        "remove": remove_profile,
        "apply": apply_profile,
        "export": export,
        "import": import_profile,
        "version": lambda args: print(f"Konsave: {VERSION}"),
        "wipe": wipe,
        "reset-config": reset_config,
        "config-check": config_check,
    }
    try:
        return funcs[args.cmd](args)
    # FIXME(urban-1): Create a "user error" exception
    except (ValueError, AssertionError) as ex:
        print(str(ex))

if __name__ == "__main__":
    main()
