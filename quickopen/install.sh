#!/bin/bash

./clean.sh
meson setup --prefix=~/.local builddir && ninja -C builddir install
