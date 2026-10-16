"""The arduino section of installer.yml, and the library.properties written from it."""

import pytest
from conftest import read

from arduino_installer import properties
from arduino_installer.core import manifest
from arduino_installer.core.manifest import ManifestError
from arduino_installer.core.target import ALREADY, CHANGED


def _loaded(library, **kwargs):
    return manifest.load(library(**kwargs))


def test_with_no_arduino_part_everything_has_a_default(library):
    text = properties.properties(_loaded(library))

    assert text.startswith(properties.MARK)
    assert "\nname=demo\nversion=1.2.0\nauthor=someone\nmaintainer=someone\nsentence=A library for the tests\n" in text
    assert "\nparagraph=\ncategory=Timing\nurl=https://github.com/someone/demo\narchitectures=*\nincludes=demo.h\n" in text
    assert "depends=" not in text


def test_the_arduino_part_is_written_as_given(library):
    loaded = _loaded(library, arduino={
        "architectures": ["avr", "esp32"], "category": "Sensors", "author": "Nima Askari",
        "maintainer": "Someone Else <x@example.com>", "depends": ["Adafruit BusIO", "ArduinoJson (>=6.0.0)"],
    })
    text = properties.properties(loaded)

    assert "author=Nima Askari\nmaintainer=Someone Else <x@example.com>\n" in text
    assert "category=Sensors\n" in text
    assert "architectures=avr,esp32\n" in text
    assert "depends=Adafruit BusIO,ArduinoJson (>=6.0.0)\n" in text


@pytest.mark.parametrize("category, expected", [
    ("sensor", "Sensors"), ("storage", "Data Storage"), ("wireless", "Communication"),
    ("input", "Signal Input/Output"), ("math", "Data Processing"), ("rtos", "Other"), ("", "Other"),
])
def test_the_category_is_the_nearest_of_arduinos(library, category, expected):
    assert properties.category(_loaded(library, extra={"category": category})) == expected


@pytest.mark.parametrize("arduino, message", [
    ({"architectures": ["a b"]}, "architectures"),
    ({"architectures": "avr esp32"}, "architectures"),
    ({"category": "Sensor"}, "Arduino's"),
    ({"author": "two\nlines"}, "one line"),
    ({"depends": ["bad;name"]}, "depends"),
    ({"depends": "Adafruit BusIO"}, "depends"),
    ("everything", "arduino should hold"),
])
def test_what_cannot_be_written_into_library_properties_is_refused(library, arduino, message):
    with pytest.raises(ManifestError, match=message):
        _loaded(library, arduino=arduino)


def test_a_single_architecture_may_be_written_alone(library):
    assert _loaded(library, arduino={"architectures": "avr"}).arduino.architectures == ["avr"]


def test_a_repository_not_on_github_has_an_unknown_author(library):
    loaded = _loaded(library, extra={"repository": "https://example.com/demo"})

    assert properties.author(loaded) == "Unknown"


def test_a_header_at_the_top_is_included_as_it_is(library):
    loaded = _loaded(library, headers=("demo.h",), sources=("demo.c",), layout="flat")

    assert properties.includes(loaded) == "demo.h"


def test_a_library_of_no_headers_has_no_includes(library):
    loaded = _loaded(library, headers=(), sources=("src/demo.c",))

    assert "includes=" not in properties.properties(loaded)


def test_it_is_written_then_left_alone(library, tmp_path):
    loaded = _loaded(library)
    folder = tmp_path / "demo"
    folder.mkdir()

    assert properties.write(loaded, folder).status == CHANGED
    assert properties.write(loaded, folder).status == ALREADY


def test_a_librarys_own_is_used_as_it_is_and_never_removed(library, tmp_path):
    folder = tmp_path / "demo"
    folder.mkdir()
    (folder / "library.properties").write_bytes(b"name=Demo\nversion=9.9.9\n")

    assert properties.write(_loaded(library), folder).status == ALREADY
    properties.remove(folder)

    assert read(folder / "library.properties") == "name=Demo\nversion=9.9.9\n"


def test_remove_takes_only_what_write_made(library, tmp_path):
    folder = tmp_path / "demo"
    folder.mkdir()
    properties.write(_loaded(library), folder)

    properties.remove(folder)

    assert not (folder / "library.properties").exists()
