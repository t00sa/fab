#!/usr/bin/env python3
##############################################################################
# (c) Crown copyright Met Office. All rights reserved.
# For further details please refer to the file COPYRIGHT
# which you should have received as part of this distribution
##############################################################################
"""
System tests for the fab command line utility.
"""

import sys
import pytest
import fab.cui.__main__


class TestArgsHandling:
    """Test the command line arguments."""

    def test_args_help(self, capsys):
        """Test list source of arguments."""

        with pytest.raises(SystemExit) as exc:
            fab.cui.__main__.main(["--help"])
        assert exc.value.code == 0

        captured = capsys.readouterr()
        assert "--file FILE" in captured.out

    def test_sys_help(self, capsys, monkeypatch):
        """Test sys.argv alternate source of arguments."""

        monkeypatch.setattr(sys, "argv", ["__main__.py", "--help"])

        with pytest.raises(SystemExit) as exc:
            fab.cui.__main__.main()
        assert exc.value.code == 0

        captured = capsys.readouterr()
        assert "--file FILE" in captured.out


class TestUserTarget:
    """Test with a user-supplied target script."""

    def test_missing_file(self, capsys):
        """Test with a missing target file."""

        with pytest.raises(SystemExit) as exc:
            fab.cui.__main__.main(["--file", "nosuch"])
        assert exc.value.code == 2

        captured = capsys.readouterr()
        assert "error: fab file does not exist" in captured.err

    def test_invalid_class_name(self, tmp_path, capsys):
        """Test with an invalid build class name."""

        target = tmp_path / "invalid.py"

        with target.open("wt", encoding="utf-8") as fd:
            print("from fab.target.base import FabTargetBase", file=fd)
            print("class FabBuildInvalidName(FabTargetBase):", file=fd)
            print("  def run(self, args):", file=fd)
            print("    pass", file=fd)

        with pytest.raises(SystemExit) as exc:
            fab.cui.__main__.main(["--file", str(target)])
        assert exc.value.code == 2

        captured = capsys.readouterr()
        assert "error: unable to find FabBuildTarget in" in captured.err

    def test_invalid_subclass(self, tmp_path, capsys):
        """Test with an invalid build class name."""

        target = tmp_path / "invalid.py"

        with target.open("wt", encoding="utf-8") as fd:
            print("class FabBuildTarget:", file=fd)
            print("  def run(self, args):", file=fd)
            print("    pass", file=fd)

        with pytest.raises(SystemExit) as exc:
            fab.cui.__main__.main(["--file", str(target)])
        assert exc.value.code == 2

        captured = capsys.readouterr()
        assert "error: FabBuildTarget is not a valid subclass" in captured.err

    def test_missing_project(self, tmp_path):
        """Test with a simple valid build class."""

        target = tmp_path / "valid.py"

        with target.open("wt", encoding="utf-8") as fd:
            print("from fab.target.base import FabTargetBase", file=fd)
            print("class FabBuildTarget(FabTargetBase):", file=fd)
            print("  def run(self, args):", file=fd)
            print("    pass", file=fd)

        with pytest.raises(SystemExit) as exc:
            fab.cui.__main__.main(["--file", str(target)])

        assert exc.value.code == 10

    def test_valid_file(self, tmp_path):
        """Test with a simple valid build class."""

        target = tmp_path / "valid.py"

        with target.open("wt", encoding="utf-8") as fd:
            print("from fab.target.base import FabTargetBase", file=fd)
            print("class FabBuildTarget(FabTargetBase):", file=fd)
            print("  project_name = 'testing'", file=fd)
            print("  def run(self, args):", file=fd)
            print("    pass", file=fd)

        fab.cui.__main__.main(["--file", str(target)])

    def test_default_file(self, tmp_path, capsys, monkeypatch):
        """Test with a valid default file."""

        target = tmp_path / "FabFile"

        with target.open("wt", encoding="utf-8") as fd:
            print("from fab.target.base import FabTargetBase", file=fd)
            print("class FabBuildTarget(FabTargetBase):", file=fd)
            print("  project_name = 'testing'", file=fd)
            print("  def run(self, args):", file=fd)
            print("    pass", file=fd)

        with monkeypatch.context() as mp:
            mp.chdir(tmp_path)
            fab.cui.__main__.main([])

        captured = capsys.readouterr()

        assert captured.err == ""
        assert captured.out == ""

    def test_interrupt_reporting(self, tmp_path):
        """Test the KeyboardInterrupt handling."""

        target = tmp_path / "valid.py"

        with target.open("wt", encoding="utf-8") as fd:
            print("from fab.target.base import FabTargetBase", file=fd)
            print("class FabBuildTarget(FabTargetBase):", file=fd)
            print("  project_name = 'testing'", file=fd)
            print("  def run(self, args):", file=fd)
            print("    raise KeyboardInterrupt()", file=fd)

        with pytest.raises(SystemExit) as exc:
            fab.cui.__main__.main(["--file", str(target)])
        assert exc.value.code == 11

    def test_invalid_import(self, tmp_path, capsys, monkeypatch):
        """Test import failure error handling."""

        target = tmp_path / "valid.py"

        with target.open("wt", encoding="utf-8") as fd:
            print("def f():", file=fd)
            print("  return True", file=fd)

        monkeypatch.setattr(fab.cui.__main__, "spec_from_loader", lambda a, b: None)

        with pytest.raises(SystemExit) as exc:
            fab.cui.__main__.main(["--file", str(target)])
        assert exc.value.code == 2

        captured = capsys.readouterr()

        assert "unable to import" in captured.err
