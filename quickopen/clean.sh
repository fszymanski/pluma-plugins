#!/bin/bash

MESON_BUILDDIR="$(dirname "$(readlink -f "$0")")/builddir"

[[ -d "$MESON_BUILDDIR" ]] && rm -r "$MESON_BUILDDIR"
