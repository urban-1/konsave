"""Konsave entry point."""

import argparse
import os
import shutil
import logging
from pkg_resources import resource_filename
from konsave.funcs import (
    list_profiles,
    save_profile,
    remove_profile,
    apply_profile,
    export,
    import_profile,
    wipe,
)
from konsave.consts import (
    VERSION,
    CONFIG_FILE,
)

logging.basicConfig(format="%(name)s: %(message)s", level=logging.INFO)


def parse_args() -> argparse.ArgumentParser:
    """
    Parses and returns all arguments
    """
    parser = argparse.ArgumentParser(
        prog="Konsave",
        epilog="Please report bugs at https://www.github.com/prayag2/konsave",
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

    export_parser = sub.add_parser("export")
    export_parser.add_argument("name")
    export_parser.add_argument("-f", "--force", action="store_true")
    export_parser.add_argument(
        "-d",
        "--directory",
        required=False,
        help="Specify the export directory when exporting a profile",
        metavar="<directory>",
    )
    export_parser.add_argument(
        "-n",
        "--export-name",
        required=False,
        help="Specify the export name when exporting a profile",
        metavar="<archive-name>",
    )

    import_parser = sub.add_parser("import")
    import_parser.add_argument("konsave-file")

    sub.add_parser("wipe")
    sub.add_parser("version")

    return parser.parse_args()


def main():
    """The main function that handles all the arguments and options."""

    if not os.path.exists(CONFIG_FILE):
        if os.path.expandvars("$XDG_CURRENT_DESKTOP") == "KDE":
            default_config_path = resource_filename("konsave", "conf_kde.yaml")
            shutil.copy(default_config_path, CONFIG_FILE)
        else:
            default_config_path = resource_filename("konsave", "conf_other.yaml")
            shutil.copy(default_config_path, CONFIG_FILE)

    args = parse_args()
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    funcs = {
        "list": list_profiles,
        "save": save_profile,
        "remove": remove_profile,
        "apply": apply_profile,
        "export": export,
        "import": import_profile,
        "version": lambda args: print(f"Konsave: {VERSION}"),
        "wipe": wipe,
    }
    return funcs[args.cmd](args)


if __name__ == "__main__":
    main()
