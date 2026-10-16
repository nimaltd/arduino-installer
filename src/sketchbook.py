"""
Where Arduino keeps its libraries, and whether a folder is a sketch.

The sketchbook is the folder the Arduino IDE and arduino-cli keep sketches in,
and its libraries folder is where Library Manager installs to and where both
look for a library a sketch includes. Where it is depends on the machine, and
on what the user set, so it is read the way Arduino reads it, first answer
wins:

    --sketchbook                    given on the command line
    ARDUINO_DIRECTORIES_USER        the variable arduino-cli reads
    ~/.arduinoIDE/arduino-cli.yaml  Arduino IDE 2's settings, directories.user
    Arduino15/arduino-cli.yaml      arduino-cli's own settings, the same key
    Arduino15/preferences.txt       Arduino IDE 1's settings, sketchbook.path
    the default                     Documents/Arduino on Windows and macOS,
                                    ~/Arduino on Linux
"""

import os
import re
import sys
from pathlib import Path

# The two keys that hold the sketchbook, in Arduino IDE 2 and arduino-cli's
# YAML, and in Arduino IDE 1's preferences.txt.
_DIRECTORIES = re.compile(r"^directories:[ \t]*\r?$", re.MULTILINE)
_USER = re.compile(r"^([ \t]+)user:[ \t]*(.*?)[ \t]*\r?$", re.MULTILINE)
_PREFERENCE = re.compile(r"^sketchbook\.path=(.*?)[ \t]*\r?$", re.MULTILINE)


def arduino15():
    """The folder Arduino keeps its own data and settings in."""
    if sys.platform == "win32":
        return Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local") / "Arduino15"

    if sys.platform == "darwin":
        return Path.home() / "Library" / "Arduino15"

    return Path.home() / ".arduino15"


def documents():
    """
    The user's Documents folder. On Windows it may have been moved, to
    OneDrive for one, which the registry says.
    """
    if sys.platform == "win32":
        try:
            import winreg

            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders") as key:
                value, _kind = winreg.QueryValueEx(key, "Personal")

            if value:
                return Path(os.path.expandvars(value))
        except OSError:
            pass

    return Path.home() / "Documents"


def default_sketchbook():
    """Where Arduino puts the sketchbook when nothing says otherwise."""
    if sys.platform.startswith("linux"):
        return Path.home() / "Arduino"

    return documents() / "Arduino"


def _unquote(value):
    """A YAML scalar without its quotes."""
    value = value.strip()

    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        value = value[1:-1]

    return value


def user_directory(text):
    """directories.user from the text of an arduino-cli.yaml, or None."""
    found = _DIRECTORIES.search(text)

    if found is None:
        return None

    # The keys indented under directories:, up to the next line at the top.
    block = text[found.end():]
    top = re.search(r"^\S", block, re.MULTILINE)
    block = block[:top.start()] if top else block
    user = _USER.search(block)

    return _unquote(user.group(2)) if user and _unquote(user.group(2)) else None


def _read(path):
    try:
        return Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def sketchbook(given=None):
    """The sketchbook folder, and where that answer came from: (Path, how)."""
    if given:
        return Path(given).expanduser().resolve(), "--sketchbook"

    variable = os.environ.get("ARDUINO_DIRECTORIES_USER")

    if variable:
        return Path(variable).expanduser().resolve(), "ARDUINO_DIRECTORIES_USER"

    for config, how in ((Path.home() / ".arduinoIDE" / "arduino-cli.yaml", "Arduino IDE's settings"),
                        (arduino15() / "arduino-cli.yaml", "arduino-cli's settings")):
        found = user_directory(_read(config))

        if found:
            return Path(found).expanduser().resolve(), how

    found = _PREFERENCE.search(_read(arduino15() / "preferences.txt"))

    if found and found.group(1).strip():
        return Path(found.group(1).strip()).expanduser().resolve(), "Arduino IDE 1's preferences"

    return default_sketchbook().resolve(), "the default"


def is_sketch(folder):
    """Whether a folder is a sketch: one with a .ino named after it, as Arduino needs."""
    folder = Path(folder)

    return (folder / f"{folder.name}.ino").is_file() or (folder / f"{folder.name}.pde").is_file()
