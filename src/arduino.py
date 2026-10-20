"""
What arduino-installer adds to the shared core: where Arduino finds a library.

Arduino has two places a library can go, and the user chooses:

    the libraries folder   of the sketchbook, where Library Manager installs.
                           Every sketch sees the library, and a library that
                           includes another finds it. The library gets a
                           library.properties, which Arduino knows it by.
    a sketch's src folder  for that sketch only, with its own settings. Arduino
                           compiles everything in it, but puts none of it on
                           the include path: the sketch includes the library by
                           its path, "src/example/example.h", and one library
                           there cannot find another.

So what a library needs always goes into the libraries folder, where any
library finds it, a library installed into a sketch included.
"""

import re
from pathlib import Path

from . import properties, sketchbook
from .core import console, installer
from .core.installer import InstallError
from .core.manifest import ManifestError
from .core.target import ALREADY, INFO, OK, WARN, Finding, Outcome, Target

LIBRARIES = "libraries"
SKETCH = "sketch"

# An architecture as boards name it in library.properties: avr, esp32,
# mbed_nano, or * for any.
ARCHITECTURE = re.compile(r"^(?:\*|[A-Za-z0-9_.-]+)$")

# A library of Library Manager's, with a version when one is needed:
# "Adafruit BusIO" or "ArduinoJson (>=6.0.0)".
DEPENDS = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 _.-]*(?: \([<>=!]*[0-9][0-9.]*\))?$")


def _text(data, key, where):
    """One line of text from the arduino section, or None."""
    value = data.get(key)

    if value is None:
        return None

    text = str(value).strip()

    if "\n" in text or "\r" in text:
        raise ManifestError(f"{where} is one line of text.")

    return text or None


class ArduinoPart:
    """The arduino section of installer.yml, with what it leaves out filled in."""

    def __init__(self, data):
        if data is None:
            data = {}

        if not isinstance(data, dict):
            raise ManifestError("arduino should hold architectures, category, author, maintainer and depends.")

        architectures = data.get("architectures") or ["*"]

        if isinstance(architectures, str):
            architectures = [architectures]

        if not isinstance(architectures, list) or not all(ARCHITECTURE.match(str(a)) for a in architectures):
            raise ManifestError(
                "arduino.architectures is a list of the architectures it runs on, such as [avr, esp32], "
                "or [\"*\"] for any."
            )

        self.architectures = [str(a) for a in architectures]
        self.category = _text(data, "category", "arduino.category")

        if self.category is not None and self.category not in properties.CATEGORIES:
            raise ManifestError(
                f"arduino.category has {self.category!r}. Use one of Arduino's: {', '.join(properties.CATEGORIES)}."
            )

        self.author = _text(data, "author", "arduino.author")
        self.maintainer = _text(data, "maintainer", "arduino.maintainer")

        depends = data.get("depends") or []

        if not isinstance(depends, list) or not all(DEPENDS.match(str(d).strip()) for d in depends):
            raise ManifestError(
                "arduino.depends is a list of Library Manager libraries by their name, such as "
                '["Adafruit BusIO"], with a version when one is needed: "ArduinoJson (>=6.0.0)".'
            )

        self.depends = [str(d).strip() for d in depends]


class Arduino(Target):
    """Arduino: the sketchbook's libraries folder, or one sketch's src folder."""

    name = "arduino-installer"
    record_name = ".arduino-installer.json"
    project = "Arduino sketch"
    requires_key = "arduino_installer"
    no_project = "Nothing was registered."
    no_project_hint = "Arduino finds a library in the libraries folder by itself."

    def __init__(self, version):
        self.version = version
        self.into = None
        self.sketchbook_given = None
        self.uninstalling = None
        self.ask = None
        # Settled by project_root() at the start of each run.
        self.libraries = None
        self.sketch = None

    # The command line

    def add_arguments(self, parser):
        parser.add_argument(
            "--into",
            choices=[LIBRARIES, SKETCH],
            default=None,
            help="where the libraries go: libraries, the sketchbook's libraries folder, for every "
            "sketch, or sketch, the src folder of the sketch this is run from, for it only. Asked "
            "when run from a sketch, libraries otherwise.",
        )
        parser.add_argument(
            "--sketchbook",
            default=None,
            metavar="FOLDER",
            help="the sketchbook folder, the one holding libraries/. Found the way Arduino finds it "
            "when not given.",
        )

    def take_arguments(self, args, ask):
        self.into = getattr(args, "into", None)
        self.sketchbook_given = getattr(args, "sketchbook", None)
        self.uninstalling = getattr(args, "uninstall", None)
        self.ask = ask
        self.sketch = None

    # Where the run works

    def _ask_where(self, sketch, libraries, default):
        """Ask which of the two places the libraries go into. Returns LIBRARIES or SKETCH."""
        if self.ask is None:
            return default

        first = "1" if default == LIBRARIES else "2"
        print()
        print(console.heading(f"This is the sketch {sketch.name}. Where do the libraries go?"))
        print(f"  1  the libraries folder, for every sketch: {libraries.as_posix()}")
        print(f"  2  this sketch's src folder, for this sketch only")
        answer = (self.ask(console.strong(f"Install into [{first}]: ")) or first).strip().lower()

        return SKETCH if answer in ("2", "s", SKETCH, "src") else LIBRARIES

    def _recorded_where(self, given, names):
        """Where the libraries to take out are recorded: SKETCH, LIBRARIES, or None."""
        in_sketch = set(installer.installed_libraries(given)) if sketchbook.is_sketch(given) else set()
        in_libraries = set(installer.installed_libraries(self.libraries))
        names = set(names)

        if names <= in_sketch:
            return SKETCH

        if names <= in_libraries:
            return LIBRARIES

        if names & in_sketch:
            raise InstallError(
                "Some of these are in this sketch and some in the libraries folder. Take them out "
                "in two runs, with --into sketch and --into libraries."
            )

        return None

    def project_root(self, given):
        """
        The libraries folder, or the sketch run from, as the user chose.

        Run from a sketch, the user is asked, and in a sketch the installer
        has put libraries into before, its src folder is the answer offered.
        Anywhere else it is the libraries folder, without a question.
        """
        found, how = sketchbook.sketchbook(self.sketchbook_given)
        self.libraries = found / "libraries"
        is_sketch = sketchbook.is_sketch(given)
        where = self.into

        if where is None and self.uninstalling:
            where = self._recorded_where(given, self.uninstalling)

        if where == SKETCH and not is_sketch:
            raise InstallError(
                f"{given.as_posix()} is not a sketch: it has no {given.name}.ino. Run this from "
                "the sketch's folder, or give it with --project."
            )

        if where is None and is_sketch and not self.uninstalling:
            used_before = bool(installer.installed_libraries(given))
            where = self._ask_where(given, self.libraries, SKETCH if used_before else LIBRARIES)

        if where == SKETCH:
            self.sketch = given
            return given

        print(console.note(f"Libraries folder: {self.libraries.as_posix()}  (from {how})"))
        self.libraries.mkdir(parents=True, exist_ok=True)

        return self.libraries

    def dependency_root(self, project_root):
        """What a library needs goes into the libraries folder, where any library finds it."""
        return self.libraries

    no_once_root = ("The libraries folder is shared by every sketch, so it has no place for them. "
                    "Install it into a sketch, with --into sketch, to get them.")

    def once_root(self, project_root):
        """
        The sketch, for a library installed into one. The libraries folder is no
        sketch's own, so there a once file, or a run step, has nowhere to go.
        """
        return None if self._in_libraries(project_root) else project_root

    def managed_files(self, project_root, library):
        """The sketch's own .ino files, which a once file must never be."""
        return [self.record_name, "*.ino"]

    def _in_libraries(self, project_root):
        return Path(project_root).resolve() == Path(self.libraries).resolve()

    def folder_for(self, library, project_root):
        """Its name in the libraries folder, src/<name> in a sketch."""
        return library.name if self._in_libraries(project_root) else f"src/{library.name}"

    def include_line(self, library, destination, project_root):
        """In a sketch, the header by its path from the sketch, which is how a sketch finds it."""
        if self._in_libraries(project_root) or not library.headers:
            return None

        header = Path(destination) / library.headers[0].destination

        try:
            return header.resolve().relative_to(Path(project_root).resolve()).as_posix()
        except ValueError:
            return None

    # installer.yml

    def read_manifest(self, manifest, data):
        manifest.arduino = ArduinoPart(data.get("arduino"))

    def read_requirements(self, requirements, data):
        """Hardware the library uses, named to the user: I2C, or I2C, 400 kHz."""
        found = []

        for entry in data.get("peripherals") or []:
            if isinstance(entry, dict):
                note = entry.get("note")
                found.append(str(entry.get("type", "")).upper() + (f", {note}" if note else ""))
            else:
                found.append(str(entry).upper())

        requirements.peripherals = found

    def requirements_empty(self, requirements):
        return not requirements.peripherals

    # Before, during and after an install

    def check(self, library, project_root):
        """What Arduino cannot do for this library, said before it goes in. Never stops an install."""
        findings = []
        in_libraries = self._in_libraries(project_root)

        if library.defines:
            findings.append(Finding(
                WARN, f"Arduino has no defines for a whole build, so these are not set: {', '.join(library.defines)}",
                f"Set them in {library.name}'s configuration header, if it has one.",
            ))

        if not in_libraries:
            for dependency in library.dependencies:
                findings.append(Finding(
                    INFO, f"{dependency.name}, which it needs, goes into the libraries folder",
                    "In a sketch's src folder one library cannot find another. In the libraries "
                    "folder every library and sketch can.",
                ))

        for name in library.arduino.depends:
            plain = name.split(" (")[0]

            if (Path(self.libraries) / plain).is_dir() or (Path(self.libraries) / plain.replace(" ", "_")).is_dir():
                findings.append(Finding(OK, f"{plain}, from Library Manager, is installed"))
            else:
                findings.append(Finding(WARN, f"Needs {plain}, from Library Manager",
                                        "Install it with the Library Manager, or arduino-cli lib install."))

        for peripheral in library.requires.peripherals:
            findings.append(Finding(INFO, f"Needs {peripheral}", "Wire it up and set it up in your sketch."))

        return findings

    def integrate(self, project_root, library, destination, only=None, dropped=(), dropped_defines=()):
        """In the libraries folder, a library.properties. In a sketch, nothing: Arduino builds src/ itself."""
        if self._in_libraries(project_root):
            return [properties.write(library, destination)]

        return [Outcome(
            "Sketch", ALREADY,
            "Arduino builds every file in the sketch's src folder, so there is nothing to register.",
        )]

    def uninstall(self, project_root, library):
        """The library.properties written for it goes, before its files do."""
        if library.destination is not None:
            properties.remove(library.destination)

        return []
