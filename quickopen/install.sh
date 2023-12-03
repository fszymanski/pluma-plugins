#!/bin/bash

[[ -d ./builddir ]] && rm -r ./builddir

meson setup --prefix=~/.local builddir && ninja -C builddir install
