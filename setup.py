#!/usr/bin/python3

from distutils.core import setup
from distutils.command.install import install
from distutils.core import Command
import subprocess, sys

version = "2.0.0"

class DebRelease(Command):
    description = 'Release a version to the debian packaging.'

    user_options = [
        ('version', None, 'Override the version to use'),
    ]

    def initialize_options(self):
        self.version = version

    def finalize_options(self):
        pass

    def run(self):
        do_deb_release(self.version)

def do_deb_release(vers):
    subprocess.run(['dch', '-v', vers])
    subprocess.run(['dch', '-r','""'])

setup(
    name = 'repoman',
    version = version,
    description = 'Easily manage software sources',
    url = 'https://github.com/isantop/repoman',
    license = 'GNU GPL3',
    packages=['repoman'],
    data_files = [
        ('/usr/share/metainfo', ['data/repoman.appdata.xml']),
        ('/usr/share/dbus-1/system-services', ['data/ro.santopiet.repoman.service']),
        ('/usr/share/polkit-1/actions', ['data/ro.santopiet.repoman.policy']),
        ('/etc/dbus-1/system.d/', ['data/ro.santopiet.repoman.conf']),
        ('/usr/share/applications', ['data/repoman.desktop']),
        ('/usr/share/repoman', ['data/style.css']),
        ('/usr/lib/repoman', ['add-del-ppa.py', 'data/repoman.pkexec'])
    ],
    scripts = ['repoman/repoman'],
    cmdclass={'release': DebRelease},
)
