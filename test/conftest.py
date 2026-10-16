"""Shared fixtures: a throwaway library repository, sketchbook and sketch."""

import importlib.util
import sys
from pathlib import Path

import pytest
import yaml

SRC = Path(__file__).resolve().parent.parent / "src"

# The package is the src folder itself, so it is loaded under its own name
# rather than found on sys.path, and before any test imports it.
if "arduino_installer" not in sys.modules:
    _spec = importlib.util.spec_from_file_location(
        "arduino_installer", SRC / "__init__.py", submodule_search_locations=[str(SRC)]
    )
    _package = importlib.util.module_from_spec(_spec)
    sys.modules["arduino_installer"] = _package
    _spec.loader.exec_module(_package)

from arduino_installer.core import cli, download  # noqa: E402

HEADER = """/**
 * @version 1.2.0
 */
#ifdef __cplusplus
extern "C" {
#endif
int {name}_answer(void);
#ifdef __cplusplus
}
#endif
"""


@pytest.fixture(autouse=True)
def sketchbook(tmp_path, monkeypatch):
    """
    A sketchbook of the test's own, given the way arduino-cli takes one, so no
    test reads or writes the machine's real one. Its folder is returned.
    """
    book = tmp_path / "Arduino"
    book.mkdir()
    monkeypatch.setenv("ARDUINO_DIRECTORIES_USER", str(book))

    return book


@pytest.fixture
def library(tmp_path):
    """
    Build a library repository on disk and return its path.

    Every argument has a working default, so a test states only the part it
    cares about. Anything in extra goes into installer.yml as it is.
    """

    def build(name="demo", headers=("src/demo.h",), sources=("src/demo.c",), arduino=None,
              requires=None, defines=None, layout="mirror", extra=None, files=None, root=None):
        root = Path(root) if root else tmp_path / "repos" / name
        root.mkdir(parents=True, exist_ok=True)

        written = {header: HEADER.replace("{name}", name) for header in headers}
        written.update({source: f"int {name}_answer(void) {{ return 42; }}\n" for source in sources})
        written.update(files or {})

        for relative, text in written.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")

        data = {
            "name": name,
            "description": "A library for the tests",
            "repository": f"https://github.com/someone/{name}",
            "category": "timing",
            "install": {"layout": layout},
            "files": {"headers": list(headers), "sources": list(sources)},
        }

        if defines:
            data["install"]["defines"] = list(defines)

        if requires is not None:
            data["requires"] = requires

        if arduino is not None:
            data["arduino"] = arduino

        data.update(extra or {})
        (root / "installer.yml").write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")

        return root

    return build


@pytest.fixture
def sketch(sketchbook):
    """A sketch in the sketchbook: a folder with a .ino named after it."""

    def build(name="blink"):
        folder = sketchbook / name
        folder.mkdir(parents=True, exist_ok=True)
        (folder / f"{name}.ino").write_text("void setup() { }\nvoid loop() { }\n", encoding="utf-8")

        return folder

    return build


@pytest.fixture
def no_network(monkeypatch):
    """Fail loudly if a test that should stay offline goes online."""

    def refuse(*args, **kwargs):
        raise AssertionError("tried to use the network")

    monkeypatch.setattr(download, "fetch", refuse)


@pytest.fixture
def nobody(monkeypatch):
    """Nobody at the keyboard: every question takes its default."""
    monkeypatch.setattr(cli, "_answer", lambda prompt: None)


@pytest.fixture
def answers(monkeypatch):
    """Answer the questions with these, in order, and keep the questions asked."""
    asked = []

    def give(*replies):
        queue = list(replies)

        def answer(prompt):
            asked.append(prompt)
            return queue.pop(0) if queue else None

        monkeypatch.setattr(cli, "_answer", answer)

        return asked

    return give


def read(path):
    """A file's bytes as text, line endings untouched."""
    return Path(path).read_bytes().decode("utf-8")
