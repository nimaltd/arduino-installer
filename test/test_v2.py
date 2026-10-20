"""
What 2.0.0 brings to Arduino: files of the project's own made once, and run
steps, in a sketch. The libraries folder is no sketch's own, so there they are
refused, with the way to get them: into a sketch.
"""

import pytest

from arduino_installer.core import cli

MODERN = {"arduino_installer": "2.0.0"}
ONCE = {"once": [{"from": "project/notes.txt"}]}
FILES = {"project/notes.txt": "mine to edit\n"}


def _install(*args):
    return cli.main([str(arg) for arg in args])


def test_in_a_sketch_a_once_file_lands_beside_the_ino(library, sketch, nobody, no_network):
    folder = sketch()

    assert _install(library(requires=MODERN, extra=ONCE, files=FILES), "--project", folder,
                    "--into", "sketch") == 0

    assert (folder / "notes.txt").read_text() == "mine to edit\n"


def test_in_the_libraries_folder_a_once_file_is_refused_naming_sketch_mode(library, sketchbook, nobody,
                                                                            no_network, capsys):
    assert _install(library(requires=MODERN, extra=ONCE, files=FILES), "--into", "libraries") == 2

    err = capsys.readouterr().err
    assert "--into sketch" in err
    assert not (sketchbook / "libraries" / "demo").exists()


def test_in_the_libraries_folder_a_run_step_is_left_unrun(library, sketchbook, nobody, no_network, capsys):
    steps = {"run": [{"label": "k", "command": ["x"]}]}

    assert _install(library(requires=MODERN, extra=steps), "--into", "libraries", "--yes") == 0

    out = capsys.readouterr().out
    assert "not run, there is no project folder here to run it in" in out
    assert "--into sketch" in out
    assert (sketchbook / "libraries" / "demo" / "library.properties").is_file()


@pytest.mark.parametrize("to", ["blink.ino", "other.ino"])
def test_a_once_file_naming_a_sketch_file_is_refused(library, sketch, nobody, no_network, to, capsys):
    folder = sketch()
    once = {"once": [{"from": "project/notes.txt", "to": to}]}

    assert _install(library(requires=MODERN, extra=once, files=FILES), "--project", folder,
                    "--into", "sketch") == 2

    assert "edits or reads as the project's own" in capsys.readouterr().err
