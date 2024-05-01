import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
# build_exe_options = {
#     "excludes": ["tkinter", "unittest"],
#     "zip_include_packages": ["encodings", "PySide6"],
# }

# base="Win32GUI" should be used only for Windows GUI app
base = "Win32GUI" if sys.platform == "win32" else None

setup(
    name="NB",
    version="1.0`",
    description="My GUI application!",
    executables=[Executable("main.py", base=base)],
)