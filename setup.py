# Original code & tutorial from sentdex:
# https://pythonprogramming.net/converting-pygame-executable-cx_freeze/

import cx_Freeze

executables = [cx_Freeze.Executable("invaders-of-space.py", base = "Win32GUI")]

cx_Freeze.setup(
    name="Invaders of Space",
    options={"build_exe": {"packages":["pgzero"],
                           "include_files":["images/","data/","sounds/"]}},
    executables = executables

    )