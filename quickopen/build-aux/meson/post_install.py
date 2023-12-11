#!/usr/bin/python3

import os
import subprocess
import sys

pkgdatadir = sys.argv[1]

if "DESTDIR" not in os.environ:
    print("Compiling python modules...")
    subprocess.run([sys.executable, "-m", "compileall", "-f", "-q", pkgdatadir])
