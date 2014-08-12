
from distutils.cmd import Command

from condiment.commands.install import Install


class Condiment(Command):

    description = ''
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        install = Install(CONDIMENTS)
        install.get_distro_data()
        install.normalize_distro_data()
        install.check_binaries()
