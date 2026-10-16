"""Where the sketchbook is, read the way Arduino reads it, and what a sketch is."""

import sys

import pytest

from arduino_installer import sketchbook


@pytest.fixture
def home(tmp_path, monkeypatch):
    """A home folder of the test's own, with nothing set, as on a fresh machine."""
    folder = tmp_path / "home"
    folder.mkdir()
    monkeypatch.delenv("ARDUINO_DIRECTORIES_USER", raising=False)
    monkeypatch.setattr(sketchbook.Path, "home", classmethod(lambda cls: folder))
    monkeypatch.setenv("LOCALAPPDATA", str(folder / "AppData" / "Local"))
    monkeypatch.setattr(sketchbook, "documents", lambda: folder / "Documents")

    return folder


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_given_comes_first(home, tmp_path, monkeypatch):
    monkeypatch.setenv("ARDUINO_DIRECTORIES_USER", str(tmp_path / "from_env"))

    found, how = sketchbook.sketchbook(str(tmp_path / "given"))

    assert found == (tmp_path / "given").resolve()
    assert how == "--sketchbook"


def test_the_variable_arduino_cli_reads_comes_next(home, tmp_path, monkeypatch):
    monkeypatch.setenv("ARDUINO_DIRECTORIES_USER", str(tmp_path / "from_env"))
    _write(home / ".arduinoIDE" / "arduino-cli.yaml", "directories:\n  user: /elsewhere\n")

    assert sketchbook.sketchbook() == ((tmp_path / "from_env").resolve(), "ARDUINO_DIRECTORIES_USER")


def test_arduino_ide_2_settings_come_before_arduino_cli(home, tmp_path):
    _write(home / ".arduinoIDE" / "arduino-cli.yaml",
           f"board_manager:\n  additional_urls: []\ndirectories:\n  data: /x\n  user: '{(tmp_path / 'ide').as_posix()}'\nlogging:\n  level: info\n")
    _write(sketchbook.arduino15() / "arduino-cli.yaml", f"directories:\n  user: {(tmp_path / 'cli').as_posix()}\n")

    assert sketchbook.sketchbook() == ((tmp_path / "ide").resolve(), "Arduino IDE's settings")


def test_arduino_cli_settings_then_ide_1_preferences(home, tmp_path):
    _write(sketchbook.arduino15() / "preferences.txt", f"sketchbook.path={(tmp_path / 'ide1').as_posix()}\r\n")

    assert sketchbook.sketchbook() == ((tmp_path / "ide1").resolve(), "Arduino IDE 1's preferences")

    _write(sketchbook.arduino15() / "arduino-cli.yaml", f'directories:\r\n  user: "{(tmp_path / "cli").as_posix()}"\r\n')

    assert sketchbook.sketchbook() == ((tmp_path / "cli").resolve(), "arduino-cli's settings")


def test_a_user_key_outside_directories_is_not_the_sketchbook(home):
    _write(home / ".arduinoIDE" / "arduino-cli.yaml", "directories:\n  data: /x\nnetwork:\n  user: /not/this\n")

    assert sketchbook.sketchbook()[1] == "the default"


def test_with_nothing_set_it_is_the_default(home):
    found, how = sketchbook.sketchbook()

    expected = home / "Arduino" if sys.platform.startswith("linux") else home / "Documents" / "Arduino"
    assert (found, how) == (expected.resolve(), "the default")


def test_a_sketch_has_a_ino_named_after_its_folder(tmp_path):
    folder = tmp_path / "blink"
    folder.mkdir()

    assert not sketchbook.is_sketch(folder)

    (folder / "other.ino").write_text("", encoding="utf-8")
    assert not sketchbook.is_sketch(folder)

    (folder / "blink.ino").write_text("", encoding="utf-8")
    assert sketchbook.is_sketch(folder)


@pytest.mark.parametrize("platform, parts", [
    ("linux", ("Arduino",)),
    ("darwin", ("Documents", "Arduino")),
    ("win32", ("Documents", "Arduino")),
])
def test_the_default_on_each_system(home, monkeypatch, platform, parts):
    monkeypatch.setattr(sketchbook.sys, "platform", platform)

    assert sketchbook.default_sketchbook() == home.joinpath(*parts)


@pytest.mark.parametrize("platform, parts", [
    ("linux", (".arduino15",)),
    ("darwin", ("Library", "Arduino15")),
    ("win32", ("AppData", "Local", "Arduino15")),
])
def test_arduino_keeps_its_settings_where_each_system_wants(home, monkeypatch, platform, parts):
    monkeypatch.setattr(sketchbook.sys, "platform", platform)

    assert sketchbook.arduino15() == home.joinpath(*parts)
