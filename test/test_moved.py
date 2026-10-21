"""This last release only says where arduino-installer went."""

import re
from pathlib import Path

from arduino_installer import __version__, cli

PYPROJECT = (Path(__file__).resolve().parent.parent / "pyproject.toml").read_text(encoding="utf-8")


def test_the_version_is_still_answered(capsys):
    assert cli.main(["--version"]) == 0
    assert capsys.readouterr().out.strip() == f"arduino-installer {__version__}"

    assert cli.main(["-V"]) == 0
    assert capsys.readouterr().out.strip() == f"arduino-installer {__version__}"


def test_a_run_says_what_to_type_and_installs_nothing(capsys):
    assert cli.main(["nimaltd/ee24", "--dir", "Libs/my ee24"]) == 1

    said = capsys.readouterr().err

    assert "arduino-installer is now lib-installer" in said
    assert "pip uninstall arduino-installer" in said
    assert "pip install lib-installer" in said
    assert "lib-installer nimaltd/ee24 --dir 'Libs/my ee24'" in said
    assert "Nothing was installed." in said


def test_a_run_with_nothing_given_says_the_same(capsys):
    assert cli.main([]) == 1
    assert "lib-installer owner/example" in capsys.readouterr().err


def test_the_command_is_still_called_arduino_installer():
    assert re.search(r'^arduino-installer = "arduino_installer\.cli:main"$', PYPROJECT, re.M)


def test_the_version_is_the_packages():
    assert __version__ == "3.0.0"
