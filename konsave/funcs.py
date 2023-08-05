"""
This module contains all the functions for konsave.
"""

import os
import logging
import shutil
import traceback
from datetime import datetime
from zipfile import is_zipfile, ZipFile
from konsave.consts import (
    HOME,
    CONFIG_FILE,
    PROFILES_DIR,
    EXPORT_EXTENSION,
    KONSAVE_DIR,
)
from konsave.parse import TOKEN_SYMBOL, tokens, parse_functions, parse_keywords

try:
    import yaml
except ModuleNotFoundError as error:
    raise ModuleNotFoundError(
        "Please install the module PyYAML using pip: \n pip install PyYAML"
    ) from error


log = logging.getLogger("Konsave")


def exception_handler(func):
    """Handles errors and prints nicely.

    Args:
        func: any function

    Returns:
        Returns function
    """

    def inner_func(*args, **kwargs):
        try:
            function = func(*args, **kwargs)
        except Exception as err:
            dateandtime = datetime.now().strftime("[%d/%m/%Y %H:%M:%S]")
            log_file = os.path.join(HOME, ".cache/konsave_log.txt")

            with open(log_file, "a", encoding="utf-8") as file:
                file.write(dateandtime + "\n")
                traceback.print_exc(file=file)
                file.write("\n")

            print(
                f"Konsave: {err}\nPlease check the log at {log_file} for more details."
            )
            return None

        return function

    return inner_func


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


@exception_handler
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


@exception_handler
def read_konsave_config(config_file) -> dict:
    """Reads "conf.yaml" and parses it.

    Args:
        config_file: path to the config file
    """
    with open(config_file, "r", encoding="utf-8") as text:
        konsave_config = yaml.load(text.read(), Loader=yaml.SafeLoader)
    parse_keywords(tokens, TOKEN_SYMBOL, konsave_config)
    parse_functions(tokens, TOKEN_SYMBOL, konsave_config)

    # in some cases conf.yaml may contain nothing in "entries". Yaml parses
    # these as NoneType which are not iterable which throws an exception
    # we can convert all None-Entries into empty lists recursively so they
    # are simply skipped in loops later on
    def convert_none_to_empty_list(data):
        if isinstance(data, list):
            data[:] = [convert_none_to_empty_list(i) for i in data]
        elif isinstance(data, dict):
            for k, v in data.items():
                data[k] = convert_none_to_empty_list(v)
        return [] if data is None else data

    return convert_none_to_empty_list(konsave_config)


@exception_handler
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
    print("ID\tNAME")
    for i, item in enumerate(profile_list):
        print(f"{i + 1}\t{item}")


@exception_handler
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
    log.info("saving profile...")
    profile_dir = os.path.join(PROFILES_DIR, name)
    mkdir(profile_dir)

    konsave_config = read_konsave_config(CONFIG_FILE)["save"]

    for section in konsave_config:
        location = konsave_config[section]["location"]
        folder = os.path.join(profile_dir, section)
        mkdir(folder)
        for entry in konsave_config[section]["entries"]:
            source = os.path.join(location, entry)
            dest = os.path.join(folder, entry)
            if os.path.exists(source):
                if os.path.isdir(source):
                    copy(source, dest)
                else:
                    shutil.copy(source, dest)

    shutil.copy(CONFIG_FILE, profile_dir)

    log.info("Profile saved successfully!")


@exception_handler
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
    profile_config = read_konsave_config(config_location)["save"]
    for name in profile_config:
        location = os.path.join(profile_dir, name)
        copy(location, profile_config[name]["location"])

    log.info(
        "Profile applied successfully! Please log-out and log-in to see the changes completely!"
    )


@exception_handler
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


@exception_handler
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
    konsave_config = read_konsave_config(profile_config_file)

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
        for entry in konsave_config_export[name]["entries"]:
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


@exception_handler
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
    konsave_config = read_konsave_config(config_file_location)

    # Copies only under "profiles"
    profile_dir = os.path.join(PROFILES_DIR, item)
    copy(os.path.join(temp_path, "save"), profile_dir)
    shutil.copy(os.path.join(temp_path, "conf.yaml"), profile_dir)

    for section in konsave_config["export"]:
        location = konsave_config["export"][section]["location"]
        path = os.path.join(temp_path, "export", section)
        mkdir(path)
        for entry in konsave_config["export"][section]["entries"]:
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


@exception_handler
def wipe():
    """Wipes all profiles."""
    confirm = input('This will wipe all your profiles. Enter "WIPE" To continue: ')
    if confirm == "WIPE":
        shutil.rmtree(PROFILES_DIR)
        log.info("Removed all profiles!")
    else:
        log.info("Aborting...")
