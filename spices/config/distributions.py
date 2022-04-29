# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.rst for a complete list of Copyright holders.
# Copyright (C) 2016-2022, Spices Developers.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

DISTRIBUTIONS = {
    'archlinux': {
        'managers': {
            'native': {
                'command': 'pacman',
                'install': '-S',
                'update': '-S',
                'args': ['--refresh', '--noconfirm', '--noprogressbar',
                         '--quiet'],
            }
        }
    },
    'alpine': {
        'managers': {
            'native': {
                'command': 'apk',
                'install': 'add',
                'update': 'update',
                'args': ['--no-progress', '--allow-untrusted', '--quiet'],
            }
        }
    },
    'debian': {
        'managers': {
            'native': {
                'env': {
                    'DEBIAN_FRONTEND': 'noninteractive'
                },
                'command': 'apt-get',
                'install': 'install',
                'update': 'update',
                'args': ['-qq', '-oApt::Install-Recommends=false',
                         '-oApt::Get::Assume-Yes=true',
                         '-oApt::Get::AllowUnauthenticated=true',
                         '-oDPkg::Options::=--force-confmiss',
                         '-oDPkg::Options::=--force-confnew',
                         '-oDPkg::Options::=--force-overwrite',
                         '-oDPkg::Options::=--force-unsafe-io'],
            }
        }
    },
    'ubuntu': {
        'managers': {
            'native': {
                'env': {
                    'DEBIAN_FRONTEND': 'noninteractive'
                },
                'command': 'apt-get',
                'install': 'install',
                'update': 'update',
                'args': ['-qq', '-oApt::Install-Recommends=false',
                         '-oApt::Get::Assume-Yes=true',
                         '-oApt::Get::AllowUnauthenticated=true',
                         '-oDPkg::Options::=--force-confmiss',
                         '-oDPkg::Options::=--force-confnew',
                         '-oDPkg::Options::=--force-overwrite',
                         '-oDPkg::Options::=--force-unsafe-io'],
            }
        }
    },
    'fedora': {
        'managers': {
            'native': {
                'command': 'yum',
                'install': 'install',
                'update': 'update',
                'args': '--assumeyes --nogpgcheck --quiet',
            }
        }
    },
    'centos': {
        'managers': {
            'native': {
                'command': 'yum',
                'install': 'install',
                'update': 'update',
                'args': '--assumeyes --nogpgcheck --quiet',
            }
        }
    },
    'gentoo': {
        'managers': {
            'native': {
                'command': 'yum',
                'install': 'install',
                'update': 'update',
                'args': '--assumeyes --nogpgcheck --quiet',
            }
        }
    }
}
