#!/usr/bin/env python3
##############################################################################
# (c) Crown copyright Met Office. All rights reserved.
# For further details please refer to the file COPYRIGHT
# which you should have received as part of this distribution
##############################################################################
"""
Logging tools for the fab framework.
"""

import logging
import inspect
from pathlib import Path


def make_logger(feature, offset=1):
    """Create a hierarchical logger.

    The name of the logger is based on the module name of the caller
    and the calling function, but with the addition of the feature
    name at the second level of the hierarchy.

    If the logger is created in a module, no function name is
    appended.  If the logger is created from the __init__ method of a
    class, the name of the class is used in place of a function.

    :param int offset: the numer of frames to skip.  Defaults to 1.
    :return: a logging.Logger instance.
    """

    # Get information about the caller using the inspect module
    finfo = inspect.stack()[offset]
    frame = finfo.frame
    code = frame.f_code
    module = inspect.getmodule(frame)
    parts = module.__name__.split(".")

    if (
        finfo.function == "__init__"
        and len(code.co_varnames)
        and code.co_varnames[0] == "self"
    ):
        # Use the class name
        parts.append(frame.f_locals["self"].__class__.__name__)
    elif finfo.function != "<module>":
        # Use the function name if not called directly in a module
        parts.append(finfo.function)

    # Clean up the name and insert the feature name
    parts = [i.replace("__", "") for i in parts]
    parts.insert(1, feature)

    # Finally assemble the logger
    return logging.getLogger(".".join(parts))


def make_loggers():
    """Create a set of named loggers.

    A simple convenience function that creates a pair of named loggers
    with build and system at the second level of the logging
    hierarchy.  This function is ignored when inspecting the calling
    tree to determine the name to use.
    """

    return make_logger("build", 2), make_logger("system", 2)


def setup_logging(build_level, system_level, quiet=False):
    """Setup the fab logging framework.

    Set output levels for build log messages and system log messages.

    Build messages are purely intended to be used to output
    information about the compile tasks.  System messages should help
    to debug the fab library itself.
    """

    # Get the hierarchical loggers
    fab_logger = logging.getLogger("fab")
    build_logger = logging.getLogger("fab.build")
    system_logger = logging.getLogger("fab.system")

    # Set log levels for user-centric build messages
    if build_level is None or build_level == 0:
        build_logger.setLevel(logging.WARNING)
    elif build_level == 1:
        build_logger.setLevel(logging.INFO)
    else:
        build_logger.setLevel(logging.DEBUG)

    # Set log levels of fab framework debug/tracing messages
    if system_level is None or system_level == 0:
        system_logger.setLevel(logging.WARNING)
    elif system_level == 1:
        system_logger.setLevel(logging.INFO)
    else:
        system_logger.setLevel(logging.DEBUG)

    # Output format includes the module if running in debug mode
    if system_level is None:
        formatter = logging.Formatter("%(asctime)s %(message)s")
    else:
        formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")

    # Create a python stream handler and set the formatting
    stream = logging.StreamHandler()
    stream.setFormatter(formatter)

    # If running in quiet mode, switch off almost everything.
    # Otherwise rely on the handler settings
    stream.setLevel(logging.ERROR if quiet else logging.DEBUG)

    # Set fab messages to use the stream handler
    fab_logger.addHandler(stream)


def setup_file_logging(logfile, parent="root", create=True):
    """Write log messages to a file.

    :param logfile: path to the output log
    :param parent: name of the logger being added
    """

    logfile = Path(logfile)

    if create:
        # Create the log directory
        logfile.parent.mkdir(parents=True, exist_ok=True)

    logfm = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logfh = logging.FileHandler(logfile)
    logfh.setLevel(logging.DEBUG)
    logfh.setFormatter(logfm)
    logging.getLogger(parent).addHandler(logfh)
