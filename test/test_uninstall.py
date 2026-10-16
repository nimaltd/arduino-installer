"""Taking a library out: from the libraries folder, or from a sketch, wherever it was put."""

from arduino_installer.core import cli, installer


def _install(*args):
    assert cli.main([str(arg) for arg in args]) == 0


def _uninstall(*args):
    return cli.main(["--uninstall"] + [str(arg) for arg in args])


def test_out_of_the_libraries_folder_with_its_library_properties(library, sketchbook, tmp_path, monkeypatch,
                                                                 nobody, no_network):
    monkeypatch.chdir(tmp_path)
    _install(library())

    assert _uninstall("demo") == 0

    assert not (sketchbook / "libraries" / "demo").exists()
    assert installer.installed_libraries(sketchbook / "libraries") == {}


def test_out_of_a_sketch_without_being_told_where(library, sketch, nobody, no_network):
    folder = sketch()
    _install(library(), "--project", folder, "--into", "sketch")

    assert _uninstall("demo", "--project", folder) == 0

    assert not (folder / "src" / "demo").exists()
    assert installer.installed_libraries(folder) == {}


def test_from_a_sketch_a_library_of_the_libraries_folder_is_found_there(library, sketch, nobody, no_network):
    folder = sketch()
    _install(library(), "--project", folder, "--into", "libraries")

    assert _uninstall("demo", "--project", folder) == 0

    assert not (folder.parent / "libraries" / "demo").exists()


def test_a_library_kept_by_one_of_the_users_own_is_left_alone(library, sketchbook, tmp_path, monkeypatch, nobody,
                                                            no_network):
    monkeypatch.chdir(tmp_path)
    _install(library(extra={"extras": ["library.properties"]},
                     files={"library.properties": "name=demo\nversion=1.2.0\n"}))

    assert _uninstall("demo") == 0

    assert not (sketchbook / "libraries" / "demo" / "src").exists()


def test_names_in_both_places_are_refused_until_split(library, sketch, nobody, no_network, tmp_path, capsys):
    folder = sketch()
    _install(library(), "--project", folder, "--into", "sketch")
    _install(library(name="helper", root=tmp_path / "repos" / "helper"), "--project", folder, "--into", "libraries")

    assert _uninstall("demo", "helper", "--project", folder) == 2

    assert "Take them out in two runs" in capsys.readouterr().err
    assert (folder / "src" / "demo").exists()
    assert (folder.parent / "libraries" / "helper").exists()
