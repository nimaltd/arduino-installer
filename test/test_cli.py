"""The whole command: where a library goes, what is asked, and what is checked first."""

import json

import pytest
from conftest import read

from arduino_installer import __version__
from arduino_installer.core import cli, installer, manifest, target
from arduino_installer.core.target import INFO, OK, WARN


def _install(*args):
    return cli.main([str(arg) for arg in args])


def _needing(library, tmp_path):
    """demo, which needs helper, both as folders on disk."""
    helper = library(name="helper", root=tmp_path / "repos" / "helper")
    demo = library(requires={"libraries": ["helper"]})

    return demo, helper


# ----------------------------------------------------------------------------
# The command
# ----------------------------------------------------------------------------


def test_the_version_is_the_packages(capsys):
    with pytest.raises(SystemExit):
        cli.main(["--version"])

    assert capsys.readouterr().out.strip() == f"arduino-installer {__version__}"


def test_the_help_offers_into_and_sketchbook(capsys):
    with pytest.raises(SystemExit):
        cli.main(["--help"])

    out = capsys.readouterr().out
    assert "--into {libraries,sketch}" in out
    assert "--sketchbook FOLDER" in out
    assert "Arduino sketch" in out


# ----------------------------------------------------------------------------
# The libraries folder
# ----------------------------------------------------------------------------


def test_outside_a_sketch_it_goes_into_the_libraries_folder(library, sketchbook, tmp_path, monkeypatch, nobody,
                                                           no_network, capsys):
    monkeypatch.chdir(tmp_path)

    assert _install(library()) == 0

    folder = sketchbook / "libraries" / "demo"
    assert (folder / "src" / "demo.h").is_file()
    assert "name=demo\n" in read(folder / "library.properties")
    assert json.loads(read(sketchbook / "libraries" / ".arduino-installer.json"))["libraries"]["demo"]["folder"] == "demo"

    out = capsys.readouterr().out
    assert f"Libraries folder: {(sketchbook / 'libraries').as_posix()}  (from ARDUINO_DIRECTORIES_USER)" in out
    assert 'Done. #include "demo.h" and you are away.' in out


def test_sketchbook_given_wins(library, tmp_path, monkeypatch, nobody, no_network):
    monkeypatch.chdir(tmp_path)
    other = tmp_path / "Other"

    assert _install(library(), "--sketchbook", other) == 0

    assert (other / "libraries" / "demo" / "library.properties").is_file()


def test_from_a_sketch_the_user_is_asked_and_the_libraries_folder_is_offered(library, sketch, answers, no_network):
    asked = answers("", "")
    folder = sketch()

    assert _install(library(), "--project", folder) == 0

    assert "Install into [1]" in asked[0]
    assert (folder.parent / "libraries" / "demo").is_dir()
    assert not (folder / "src").exists()


def test_nobody_there_means_the_libraries_folder(library, sketch, nobody, no_network):
    folder = sketch()

    assert _install(library(), "--project", folder) == 0

    assert (folder.parent / "libraries" / "demo").is_dir()


# ----------------------------------------------------------------------------
# A sketch's src folder
# ----------------------------------------------------------------------------


@pytest.mark.parametrize("answer", ["2", "sketch", "S"])
def test_answered_sketch_it_goes_into_src(library, sketch, answers, no_network, answer, capsys):
    answers(answer, "")
    folder = sketch()

    assert _install(library(), "--project", folder) == 0

    assert (folder / "src" / "demo" / "src" / "demo.h").is_file()
    assert not (folder / "src" / "demo" / "library.properties").exists()
    assert "demo" in installer.installed_libraries(folder)
    out = capsys.readouterr().out
    assert 'Done. #include "src/demo/src/demo.h" and you are away.' in out
    assert "nothing to register" in out


def test_a_sketch_already_used_offers_its_src_folder(library, sketch, answers, nobody, no_network):
    folder = sketch()
    assert _install(library(), "--project", folder, "--into", "sketch") == 0
    asked = answers("", "")

    assert _install(library(name="other", headers=("src/other.h",), sources=()), "--project", folder) == 0

    assert "Install into [2]" in asked[0]
    assert (folder / "src" / "other" / "src" / "other.h").is_file()


def test_into_sketch_outside_a_sketch_is_refused(library, tmp_path, monkeypatch, no_network, capsys):
    monkeypatch.chdir(tmp_path)

    assert _install(library(), "--into", "sketch") == 2

    assert "is not a sketch: it has no" in capsys.readouterr().err


def test_what_a_library_in_a_sketch_needs_goes_into_the_libraries_folder(library, sketch, nobody, no_network,
                                                                        tmp_path, capsys):
    folder = sketch()
    demo, helper = _needing(library, tmp_path)

    assert _install(demo, helper, "--project", folder, "--into", "sketch") == 0

    assert (folder / "src" / "demo" / "src" / "demo.h").is_file()
    assert (folder.parent / "libraries" / "helper" / "library.properties").is_file()
    assert not (folder / "src" / "helper").exists()
    assert "helper, which it needs, goes into the libraries folder" in capsys.readouterr().out


def test_what_is_in_the_libraries_folder_already_is_kept(library, sketch, nobody, no_network, tmp_path, capsys):
    folder = sketch()
    demo, helper = _needing(library, tmp_path)
    assert _install(helper, "--project", folder, "--into", "libraries") == 0

    assert _install(demo, "--project", folder, "--into", "sketch") == 0

    assert "helper 1.2.0 is already in this project, kept" in capsys.readouterr().out


# ----------------------------------------------------------------------------
# What is checked before the library goes in
# ----------------------------------------------------------------------------


def _check(library, root, **kwargs):
    return target.current.check(manifest.load(library(**kwargs)), root)


@pytest.fixture
def libraries_mode(sketchbook, tmp_path, monkeypatch):
    """The target settled on the libraries folder, as a run outside a sketch leaves it."""
    monkeypatch.chdir(tmp_path)
    target.current.take_arguments(type("A", (), {"into": None, "sketchbook": None, "uninstall": None})(), None)

    return target.current.project_root(tmp_path)


def test_defines_are_said_to_have_no_place(library, libraries_mode):
    found = _check(library, libraries_mode, defines=["DEMO_FAST", "DEMO_N=2"])

    assert [(f.level, f.message) for f in found] == [
        (WARN, "Arduino has no defines for a whole build, so these are not set: DEMO_FAST, DEMO_N=2")]


def test_library_manager_libraries_are_looked_for(library, libraries_mode):
    (libraries_mode / "Adafruit_BusIO").mkdir()

    found = _check(library, libraries_mode, arduino={"depends": ["Adafruit BusIO", "ArduinoJson (>=6.0.0)"]},
                   requires={"peripherals": [{"type": "i2c", "note": "400 kHz"}, "spi"]})

    assert [(f.level, f.message) for f in found] == [
        (OK, "Adafruit BusIO, from Library Manager, is installed"),
        (WARN, "Needs ArduinoJson, from Library Manager"),
        (INFO, "Needs I2C, 400 kHz"),
        (INFO, "Needs SPI"),
    ]


def test_in_the_libraries_folder_a_dependency_is_not_mentioned(library, libraries_mode):
    assert _check(library, libraries_mode, requires={"libraries": ["helper"]}) == []


def test_with_nobody_to_ask_the_default_is_taken(sketch):
    arduino = target.current
    arduino.ask = None

    assert arduino._ask_where(sketch(), sketch().parent / "libraries", "libraries") == "libraries"
    assert arduino._ask_where(sketch(), sketch().parent / "libraries", "sketch") == "sketch"
