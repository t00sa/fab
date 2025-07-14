#!/usr/bin/env python3
##############################################################################
# (c) Crown copyright Met Office. All rights reserved.
# For further details please refer to the file COPYRIGHT
# which you should have received as part of this distribution
##############################################################################
"""
Unit tests for fab.logtools.
"""


import logging
from fab.logtools import make_logger, make_loggers, setup_logging, setup_file_logging

import pytest


class TestCreateLoggers:
    """Check creation of loggers works as expected."""

    def test_function_logger(self):
        """Create a single logger in the build hierarchy."""

        logger = make_logger("build")
        assert isinstance(logger, logging.Logger)
        assert ".build." in logger.name
        assert logger.name.endswith(".test_function_logger")

    def test_class_logger(self):
        """Create a logger inside an instance."""

        class MyClass:
            """Example class."""

            def __init__(self):
                self.logger = make_logger("build")

        m = MyClass()
        assert isinstance(m.logger, logging.Logger)
        assert ".build." in m.logger.name
        assert m.logger.name.endswith(".MyClass")

    def test_multiple_loggers(self):
        """Create build and system loggers."""

        loggers = make_loggers()
        assert len(loggers) == 2
        assert all(isinstance(i, logging.Logger) for i in loggers)
        assert ".build." in loggers[0].name
        assert ".system." in loggers[1].name
        assert loggers[0].name.endswith(".test_multiple_loggers")
        assert loggers[1].name.endswith(".test_multiple_loggers")


class TestSetupLogging:

    @pytest.mark.parametrize(
        "blevel,slevel,expected",
        [
            (0, 0, set([])),
            (1, 0, set(["build info"])),
            (2, 0, set(["build info", "build debug"])),
            (0, 1, set(["system info"])),
            (0, 2, set(["system info", "system debug"])),
        ],
        ids=["nothing", "build info", "build debug", "system info", "system debug"],
    )
    def test_levels(self, blevel, slevel, expected, caplog, capsys):

        build_logger = logging.getLogger("fab.build")
        system_logger = logging.getLogger("fab.system")

        setup_logging(blevel, slevel, False)
        build_logger.info("build info")
        build_logger.debug("build debug")

        system_logger.info("system info")
        system_logger.debug("system debug")

        count = 0
        for entry in expected:
            if entry in caplog.text:
                count += 1

        assert count == len(expected)

    # FIXME: this needs to capture the output from the stream handler
    # and confirm that it has been filtered correctly.  Using
    # caplog.text gets all the messages, not just the one that have
    # made it to the output handler.
    #
    # @pytest.mark.parametrize(
    #     "blevel,slevel",
    #     [
    #         (0, 0),
    #         (1, 0),
    #         (2, 0),
    #         (0, 1),
    #         (0, 2),
    #     ],
    #     ids=["nothing", "build info", "build debug", "system info", "system debug"],
    # )
    # def test_quiet(self, blevel, slevel, caplog):

    #     build_logger = logging.getLogger("fab.build")
    #     system_logger = logging.getLogger("fab.system")

    #     setup_logging(blevel, slevel, True)
    #     build_logger.warning("build warning")
    #     build_logger.info("build info")
    #     build_logger.debug("build debug")

    #     system_logger.info("system info")
    #     system_logger.debug("system debug")

    #     assert "build warning" in caplog.text
    #     assert "build info" not in caplog.text
    #     assert "build debug" not in caplog.text
    #     assert "system info" not in caplog.text
    #     assert "system debug" not in caplog.text


def test_file_logging(tmp_path, caplog):

    logfile = tmp_path / "subdir" / "test.log"
    setup_file_logging(logfile)
    assert logfile.is_file()
