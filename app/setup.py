#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

from cx_Freeze import setup, Executable


def files_under_dir(dir_name):
    file_list = []
    for root, dirs, files in os.walk(dir_name):
        for name in files:
            file_list.append(os.path.join(root, name))
    return file_list


includefiles = []
for directory in ("static", "templates", "modules", "config"):
    includefiles.extend(files_under_dir(directory))

# base = None
base = "Win32GUI"

build_options = {
          "build_exe": {
              "packages": ["requests",
                           "PIL",
                           "tornado",
                           "desktopmagic",
                           "jinja2"],
              "excludes": ["jinja2.asyncfilters", "jinja2.asyncsupport",
                           "tkinter", "collections.sys",
                           "collections._weakref"],
              "include_files": includefiles,
              "include_msvcr": True}}

main_executable = Executable("ScreenBloom.py", base=base, icon="static/images/icon.ico")
setup(name="ScreenBloom",
      version="2.2",
      description="ScreenBloom",
      options=build_options,
      executables=[main_executable])
