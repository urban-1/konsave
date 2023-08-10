## WARNINGS 

1. This is a fork of https://github.com/Prayag2/konsave that was heavily refactored
1. Code here is no longer compatible with parent project which means that any improvements there will need to be manually ported to this version


---

<h1 align=center> Konsave (Save Linux Customization) </h1>
<p align=center>A CLI program that will let you save and apply your Linux customizations with just one command! Konsave also lets you share your dot files to your friends in an instant! It officially supports KDE Plasma but it can be used on all other desktop environments too!</p>

---

## Installation

```
pip install konsave-urban
```

## Usage
### Get Help

```
$ konsave -h
usage: Konsave [-h] [-d] {list,save,remove,apply,export,import,wipe,version,reset-config,config-check} ...

positional arguments:
  {list,save,remove,apply,export,import,wipe,version,reset-config,config-check}
    export              Export a profile to a konsave archive
    import              Import a profile from a konsave archive
    wipe                Wipe all profiles - this cannot be undone!
    version             Show Konsave version
    reset-config        Reset the konsave config to the factory default. This option is mainly useful for development
    config-check        Check currect config against ~/.config folders/files and show what is backed up and what is not

options:
  -h, --help            show this help message and exit
  -d, --debug           Enable debug logging

Please report bugs at https://www.github.com/urban-1/konsave
```

### Save current configuration as a profile

```
$ konsave save test
Konsave: Saving profile...
Konsave: Profile saved successfully!
```

#### Overwrite an already saved profile

Normally you would get:

```
$ konsave save test
Traceback (most recent call last):
  File "/home/urban/git/konsave/.venv/bin/konsave", line 33, in <module>
    sys.exit(load_entry_point('Konsave', 'console_scripts', 'konsave')())
  File "/home/urban/git/konsave/konsave/__main__.py", line 127, in main
    return funcs[args.cmd](args)
  File "/home/urban/git/konsave/konsave/funcs.py", line 131, in save_profile
    args.name not in profile_list or args.force
AssertionError: Profile with this name already exists
```

if you want to overwrite that is there:

```
$ konsave save test -f
Konsave: Saving profile...
Konsave: Profile saved successfully!
$ konsave save test --force
Konsave: Saving profile...
Konsave: Profile saved successfully!
```

### List all profiles

```
$ konsave list
Konsave profiles:
  ID  NAME
----  -------
   0  test
```

### Remove a profile
```
$ konsave remove test
Konsave: removing profile...
Konsave: removed profile successfully
```

### Apply a profile

```
konsave apply test
```

If you are a KDE user, you can supply `-r/--reload-kde` which will invoke a `killall plasmashell; kstart plasmashell` to restart plasma and pick up the changes.

You may need to log out and log in to see all the changes.  

### Export a profile as a ".knsv" file to share it with your friends!

```
konsave export <profile name>
``` 

If the target file already exists, the date will be automatically appended to the archive name. If you want to overwrite the existing file use `-f/--force`

You can also specify a different output file using the `-o/--output` flag, for example:

```
konsave export trigkey -o /tmp/test.knsv

# OR dump archive on screen
konsave export trigkey -o /dev/stdout
```

### Import a ".knsv" file
```
konsave import <path to the file>
```

If you want to import under a different name (other than the knsv filename) use `--import-name`

### Show current version
`konsave version`

### Wipe all profiles
`konsave wipe`

  
---
  

## Editing the configuration file
You can make changes to Konsave's configuration file according to your needs. The configuration file is located in `~/.config/konsave/conf.yaml`.
When using Konsave for the first time, you'll be prompted to enter your desktop environment.  
For KDE Plasma users, the configuration file will be pre-configured.

### The Format
```yaml
---
save:
    # This inludes configs. All files listed here are being re-installed
    # when one calls konsave apply <profile> (overwriting existing user
    # configs)
    name:
        location: "path/to/parent/directory"
        entries: 
        # these are files which will be backed up. 
        # They should be present in the specified location.
            - file1
            - file2
export:
    # This includes files which will be exported with your profile archive.
    # These will not be copied over on "apply" but only on import. Ideally
    # this section should include files like icon packs, themes, fonts
    name:
        location: "path/to/parent/directory"
        entries: 
            - file1
            - file2
...
```
You can use these placeholders in the "location" of each item:
- `$HOME`: the home directory
- `$CONFIG_DIR`: refers to "$HOME/.config/"
- `$SHARE_DIR`: refers to "$HOME/.local/share"
- `$BIN_DIR`: refers to "$HOME/.local/bin"
- `${ENDS_WITH="text"}`: for folders with different names on different computers whose names end with the same thing.


---

## Contributing
Please read [CONTRIBUTION.md](https://github.com/urban-1/konsave/blob/master/CONTRIBUTION.md) for info about contributing. 

## License
This project uses GNU General Public License 3.0
