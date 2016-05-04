#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
# import sys

from cx_Freeze import setup, Executable


def files_under_dir(dir_name):
    file_list = []
    for root, dirs, files in os.walk(dir_name):
        for name in files:
            file_list.append(os.path.join(root, name))
    return file_list


includefiles = []
for directory in ('static', 'templates', 'modules'):
    includefiles.extend(files_under_dir(directory))

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
# if sys.platform == "win32":
#     base = "Win32GUI"

main_executable = Executable("ScreenBloom.py", base=base, icon="static/images/icon.ico")
setup(name="ScreenBloom",
      version="1.5",
      description="ScreenBloom",
      options={
          'build_exe': {
              'packages': ['requests',
                           'beautifulhue',
                           'PIL'],
              'include_files': includefiles,
              'include_msvcr': True}},
      executables=[main_executable])