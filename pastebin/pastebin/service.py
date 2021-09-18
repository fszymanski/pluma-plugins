# Copyright (C) 2021 Filip Szymański <fszymanski.pl@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#

try:
    import gettext

    gettext.bindtextdomain('pluma-plugins')
    gettext.textdomain('pluma-plugins')
    _ = gettext.gettext
except:
    _ = lambda s: s

from urllib.parse import urlparse

import gi

gi.require_version('Pluma', '1.0')
from gi.repository import Pluma

import requests


class Service():
    @staticmethod
    def upload(paste_code, paste_name, paste_format, paste_private, paste_expire_date):
        api_url = 'https://pastebin.com/api/api_post.php'
        body = {
            'api_dev_key': 'FcF09F1d1Okxe0LX60ZfHo6BklWjJnyE',
            'api_option': 'paste',
            'api_paste_code': paste_code,
            'api_paste_name': paste_name,
            'api_paste_format': paste_format,
            'api_paste_private': paste_private,
            'api_paste_expire_date': paste_expire_date
        }
        headers = {'User-Agent': f'Pluma/{Pluma._version}'}

        res = requests.post(api_url, data=body, headers=headers, timeout=60, allow_redirects=False)
        res.raise_for_status()

        link = res.text
        if not urlparse(link).scheme:
            raise TypeError(_('No URL scheme'))

        return link

# vim: ts=4 et
