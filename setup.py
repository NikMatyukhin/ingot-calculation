import os
import sys
import importlib

from cx_Freeze import setup, Executable

pyside6_path = list(importlib.import_module('PySide6').__path__)[0]
plugins_path = os.path.join(pyside6_path, "plugins")
shiboken6_path = list(importlib.import_module('shiboken6').__path__)[0]

base = None
if sys.platform == "win32":
    base = "Win32GUI"

options = {
    "build_exe": {
        "includes": [
            "shiboken6",
            "PySide6"
        ], # packages must be in the build
        "include_files": [
            os.path.join(plugins_path, "platforms"),
            "charts/", "data/", "gui/", "sequential_mh/", "schemes/",
            "application_rc.py",
            "catalog.py",
            "dialogs.py",
            "models.py",
            "service.py",
            "settings.py",
            "widgets.py",
            shiboken6_path,
            pyside6_path
        ],  # additional plugins needed by qt at runtime
        "zip_include_packages": [
            "PySide6",
            "shiboken6",
            "encodings",
        ],  # reduce size of packages that are used
        "excludes": [
            "tkinter",
            "unittest",
            "email",
            "http",
            "pydoc",
            "pdb",
        ],  # exclude packages that are not really needed
    }
}

executables = [Executable("mainwindow.py", base=base, icon="gui/resources/kras-logo.ico", target_name="OCI")]

setup(
    name="OCI",
    version="1.0",
    description="No description",
    options=options,
    executables=executables,
)