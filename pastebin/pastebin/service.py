# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2021-2023 Filip Szymański <fszymanski.pl@gmail.com>

import platform
from urllib.parse import urlparse

import gi

gi.require_version("Pluma", "1.0")
from gi.repository import Pluma

import requests

uname = platform.uname()


class Service:
    @staticmethod
    def upload(paste_code, paste_name, paste_format, paste_private, paste_expire_date):
        api_url = "https://pastebin.com/api/api_post.php"
        body = {
            "api_dev_key": "FcF09F1d1Okxe0LX60ZfHo6BklWjJnyE",
            "api_option": "paste",
            "api_paste_code": paste_code,
            "api_paste_name": paste_name,
            "api_paste_format": paste_format,
            "api_paste_private": paste_private,
            "api_paste_expire_date": paste_expire_date
        }
        headers = {"User-Agent": f"Pluma/{Pluma._version} ({uname.system} {uname.machine})"}

        res = requests.post(api_url, data=body, headers=headers, timeout=60, allow_redirects=False)
        res.raise_for_status()

        link = res.text
        if not urlparse(link).scheme:
            raise TypeError("No URL scheme")

        return link
