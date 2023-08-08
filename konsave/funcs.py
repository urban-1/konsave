"""
This module contains all the functions for konsave.
"""

import os
import logging
import shutil
from datetime import datetime
from zipfile import is_zipfile, ZipFile
from pkg_resources import resource_filename

import tabulate

from konsave.consts import (
    CONFIG_DIR,
    CONFIG_FILE,
    PROFILES_DIR,
    EXPORT_EXTENSION,
    KONSAVE_DIR,
)
from konsave.config import parse


log = logging.getLogger("Konsave")


def get_profiles():
    """Return the profile names installed/saved and their count"""
    profs = os.listdir(PROFILES_DIR)
    return profs, len(profs)


def mkdir(path):
    """Creates directory if it doesn't exist.

    Args:
        path: path to the new directory

    Returns:
        path: the same path
    """
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def copy(source, dest):
    """
    This function was created because shutil.copytree gives error if the
    destination folder exists and the argument "dirs_exist_ok" was introduced
    only after python 3.8.

    This restricts people with python 3.7 or less from using Konsave.
    It uses recursion to copy files and folders from "source" to "dest"

    Args:
        source: the source destination
        dest: the destination to copy the file/folder to
    """
    assert isinstance(source, str) and isinstance(dest, str), "Invalid path"
    assert source != dest, "Source and destination can't be same"
    assert os.path.exists(source), "Source path doesn't exist"

    if not os.path.exists(dest):
        os.mkdir(dest)

    for item in os.listdir(source):
        source_path = os.path.join(source, item)
        dest_path = os.path.join(dest, item)

        if os.path.isdir(source_path):
            copy(source_path, dest_path)
            continue

        if os.path.exists(dest_path):
            os.remove(dest_path)
        if os.path.exists(source_path):
            shutil.copy(source_path, dest)


def list_profiles(args):  # pylint: disable=unused-argument
    """Lists all the created profiles.

    Args:
        profile_list: the list of all created profiles
        profile_count: number of profiles created
    """
    profile_list, profile_count = get_profiles()

    # assert
    assert os.path.exists(PROFILES_DIR) and profile_count != 0, "No profile found."

    # run
    print("Konsave profiles:")
    print(
        tabulate.tabulate(
            [[i, item] for i, item in enumerate(profile_list)], headers=["ID", "NAME"]
        )
    )


def save_profile(args):
    """Saves necessary config files in ~/.config/konsave/profiles/<name>.

    Args:
        name: name of the profile
        profile_list: the list of all created profiles
        force: force overwrite already created profile, optional
    """
    name = args.name
    profile_list, _ = get_profiles()

    # assert
    assert (
        args.name not in profile_list or args.force
    ), "Profile with this name already exists"

    # run
    log.info("Saving profile...")
    profile_dir = os.path.join(PROFILES_DIR, name)
    mkdir(profile_dir)

    konsave_config = parse(CONFIG_FILE)["save"]

    for section_name, section in konsave_config.items():
        log.debug(f" - Processing {section_name}")
        folder = os.path.join(profile_dir, section_name)
        mkdir(folder)
        for entry in section["entries"] or ():
            source = os.path.join(section["location"], entry)
            dest = os.path.join(folder, entry)
            if not os.path.exists(source):
                log.debug(f"File {source} does not exist")
                continue

            if os.path.isdir(source):
                copy(source, dest)
            else:
                shutil.copy(source, dest)

    shutil.copy(CONFIG_FILE, profile_dir)

    log.info("Profile saved successfully!")


def apply_profile(args):
    """Applies profile of the given id.

    Args:
        profile_name: name of the profile to be applied
        profile_list: the list of all created profiles
        profile_count: number of profiles created
    """

    profile_list, profile_count = get_profiles()
    # assert
    assert profile_count != 0, "No profile saved yet."
    assert args.name in profile_list, "Profile not found :("

    # run
    profile_dir = os.path.join(PROFILES_DIR, args.name)

    log.info("copying files...")

    config_location = os.path.join(profile_dir, "conf.yaml")
    profile_config = parse(config_location)["save"]
    for name in profile_config:
        location = os.path.join(profile_dir, name)
        copy(location, profile_config[name]["location"])

    log.info(
        "Profile applied successfully! Please log-out and log-in to see the changes completely!"
    )


def remove_profile(args):
    """Removes the specified profile.

    Args:
        profile_name: name of the profile to be removed
        profile_list: the list of all created profiles
        profile_count: number of profiles created
    """

    profile_list, profile_count = get_profiles()
    # assert
    assert profile_count != 0, "No profile saved yet."
    assert args.name in profile_list, "Profile not found."

    # run
    log.info("removing profile...")
    shutil.rmtree(os.path.join(PROFILES_DIR, args.name))
    log.info("removed profile successfully")


def export(args):
    """It will export the specified profile as a ".knsv" to the specified directory.
       If there is no specified directory, the directory is set to the current working directory.

    Args:
        profile_name: name of the profile to be exported
        profile_list: the list of all created profiles
        profile_count: number of profiles created
        directory: output directory for the export
        force: force the overwrite of existing export file
        name: the name of the resulting archive
    """

    profile_name = args.name
    profile_list, profile_count = get_profiles()
    archive_dir = args.directory
    archive_name = args.name
    # assert
    assert profile_count != 0, "No profile saved yet."
    assert profile_name in profile_list, "Profile not found."

    # run
    profile_dir = os.path.join(PROFILES_DIR, profile_name)

    if archive_name:
        profile_name = archive_name

    if archive_dir:
        export_path = os.path.join(archive_dir, profile_name)
    else:
        export_path = os.path.join(os.getcwd(), profile_name)

    # Only continue if export_path, export_path.ksnv and export_path.zip don't exist
    # Appends date and time to create a unique file name
    if not args.force:
        while True:
            paths = [f"{export_path}", f"{export_path}.knsv", f"{export_path}.zip"]
            if any(os.path.exists(path) for path in paths):
                time = f"{datetime.now():%d-%m-%Y:%H-%M-%S}"
                export_path = f"{export_path}_{time}"
            else:
                break

    # compressing the files as zip
    log.info("Exporting profile. It might take a minute or two...")

    profile_config_file = os.path.join(profile_dir, "conf.yaml")
    konsave_config = parse(profile_config_file)

    export_path_save = mkdir(os.path.join(export_path, "save"))
    for name in konsave_config["save"]:
        location = os.path.join(profile_dir, name)
        log.info(f'Exporting "{name}"...')
        copy(location, os.path.join(export_path_save, name))

    konsave_config_export = konsave_config["export"]
    export_path_export = mkdir(os.path.join(export_path, "export"))
    for name in konsave_config_export:
        location = konsave_config_export[name]["location"]
        path = mkdir(os.path.join(export_path_export, name))
        for entry in konsave_config_export[name]["entries"] or ():
            source = os.path.join(location, entry)
            dest = os.path.join(path, entry)
            log.info(f'Exporting "{entry}"...')
            if os.path.exists(source):
                if os.path.isdir(source):
                    copy(source, dest)
                else:
                    shutil.copy(source, dest)

    shutil.copy(CONFIG_FILE, export_path)

    log.info("Creating archive")
    shutil.make_archive(export_path, "zip", export_path)

    shutil.rmtree(export_path)
    shutil.move(export_path + ".zip", export_path + EXPORT_EXTENSION)

    log.info(f"Successfully exported to {export_path}{EXPORT_EXTENSION}")


def import_profile(args):
    """This will import an exported profile.

    Args:
        path: path of the `.knsv` file
    """
    path = args.path
    # assert
    assert (
        is_zipfile(path) and path[-5:] == EXPORT_EXTENSION
    ), "Not a valid konsave file"
    item = os.path.basename(path)[:-5]
    assert not os.path.exists(
        os.path.join(PROFILES_DIR, item)
    ), "A profile with this name already exists"

    # run
    log.info("Importing profile. It might take a minute or two...")

    item = os.path.basename(path).replace(EXPORT_EXTENSION, "")

    temp_path = os.path.join(KONSAVE_DIR, "temp", item)

    with ZipFile(path, "r") as zip_file:
        zip_file.extractall(temp_path)

    config_file_location = os.path.join(temp_path, "conf.yaml")
    konsave_config = parse(config_file_location)

    # Copies only under "profiles"
    profile_dir = os.path.join(PROFILES_DIR, item)
    copy(os.path.join(temp_path, "save"), profile_dir)
    shutil.copy(os.path.join(temp_path, "conf.yaml"), profile_dir)

    for section in konsave_config["export"]:
        location = konsave_config["export"][section]["location"]
        path = os.path.join(temp_path, "export", section)
        mkdir(path)
        for entry in konsave_config["export"][section]["entries"] or ():
            source = os.path.join(path, entry)
            dest = os.path.join(location, entry)  # Installs into the location ??
            log.info(f'Importing "{entry}"...')
            if os.path.exists(source):
                if os.path.isdir(source):
                    copy(source, dest)
                else:
                    shutil.copy(source, dest)

    shutil.rmtree(temp_path)

    log.info("Profile successfully imported!")


def config_check(args):  # pylint: disable=unused-argument
    """Compare konsave config with user's ~/.config"""

    konsave_config = parse(CONFIG_FILE)

    dir_entries = set(os.listdir(CONFIG_DIR))

    for name, section in konsave_config["save"].items():
        if not section["location"] == CONFIG_DIR:
            continue

        print(f"\n# Config section: {name}\n")
        entries = set(section["entries"])
        table = []
        for entry in sorted(entries | dir_entries):
            table.append([entry, entry in entries, entry in dir_entries])
        print(tabulate.tabulate(table, headers=["Entry", "Backed Up?", "In ~/.config"]))


def wipe():
    """Wipes all profiles."""
    confirm = input('This will wipe all your profiles. Enter "WIPE" To continue: ')
    if confirm == "WIPE":
        shutil.rmtree(PROFILES_DIR)
        log.info("Removed all profiles!")
    else:
        log.info("Aborting...")


def install_config(force: bool = False):
    """
    Install the main konsave config into the user's ~/.config folder.
    If force is True, it will delete any existing config and overwrite
    with the distributed one.
    """
    if os.path.exists(CONFIG_FILE) and force:
        os.unlink(CONFIG_FILE)

    if os.path.exists(CONFIG_FILE):
        return

    if os.path.expandvars("$XDG_CURRENT_DESKTOP") == "KDE":
        default_config_path = resource_filename("konsave", "conf_kde.yaml")
        shutil.copy(default_config_path, CONFIG_FILE)
    else:
        default_config_path = resource_filename("konsave", "conf_other.yaml")
        shutil.copy(default_config_path, CONFIG_FILE)


def reset_config(args):  # pylint: disable=unused-argument
    """
    Subcommand compliant entrypoint to delete and re-deploy config
    """
    install_config(force=True)
