import os
import argparse


class Parser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(add_help=False)
        self.parser.add_argument('--help', action="help")
        self.parser.add_argument('-c', '--config', metavar="FILENAME",
                                 default=os.path.join(os.getcwd(), ".pgv"),
                                 help="main configuration file")
        self.commands = self.parser.add_subparsers(dest="command")
        self.add_init()
        self.add_make()
        self.add_install()
        self.add_skip()
        self.add_show()

    def add_connection(self, parser, required=False):
        if required:
            title = "database connection arguments"
        else:
            title = "optional database connection arguments"

        g = parser.add_argument_group(title=title)
        g.add_argument('-d', '--dbname', required=required)
        g.add_argument('-h', '--host')
        g.add_argument('-p', '--port')
        g.add_argument('-U', '--username')
        g.add_argument('-w', '--no-password', dest="prompt_password",
                       action="store_false", default=False)
        g.add_argument('-W', '--password', dest="prompt_password",
                       action="store_true", default=False)

    def add_version(self, parser):
        g = parser.add_argument_group(title="optional version arguments")
        g.add_argument('-f', '--from', dest="from_rev", metavar="REVISION")
        g.add_argument('-t', '--to', dest="to_rev", metavar="REVISION")

    def add_package(self, parser):
        g = parser.add_argument_group(title="optional package arguments")
        g.add_argument('-o', '--output', metavar="PATH")
        g.add_argument('-F', '--format',
                       choices=("tar", "tar.gz", "tar.bz2", "directory"))

    def add_init(self):
        usage = """
    pgv init [--help]
    pgv init [-o] [-d DBNAME] [-h HOST] [-p PORT] [-U USERNAME] [-w|-W]
        """

        init = self.commands.add_parser(
            'init', add_help=False, usage=usage,
            help="init versioning schema in database")
        init.add_argument('--help', action="help")
        init.add_argument('-o', '--overwrite', action="store_true",
                          help="overwrite if schema exists")
        self.add_connection(init)

    def add_make(self):
        usage = """
    pgv make [--help]
    pgv make [-f REVISION] [-t REVISION] [-o PATH] [-F FORMAT]
    pgv make -d DBNAME [-h HOST] [-p PORT] [-U USERNAME] [-w|-W] \
[-t REVISION] [-o PATH] [-F FORMAT]
        """

        make = self.commands.add_parser('make', add_help=False,
                                        help="make package",
                                        usage=usage)
        make.add_argument('--help', action="help")
        self.add_package(make)
        self.add_version(make)
        self.add_connection(make)

    def add_install(self):
        usage = """
    pgv install [--help]
    pgv install [--devel] -d DBNAME [-h HOST] [-p PORT] [-U USERNAME] [-w|-W] \
[-i PATH] [ -F FORMAT]
        """

        install = self.commands.add_parser('install', add_help=False,
                                           help="install package to database",
                                           usage=usage)
        install.add_argument('--help', action="help")
        install.add_argument('--devel', action="store_true",
                             help="install schema from working directory")
        self.add_package(install)
        #self.add_version(install)
        self.add_connection(install, True)

    def add_skip(self):
        usage = """
    pgv skip [--help]
    pgv skip [[-f FILENAME],...] revision
        """

        skip = self.commands.add_parser('skip', add_help=False,
                                        help="skip revision from package",
                                        usage=usage)
        skip.add_argument('--help', action="help")
        skip.add_argument('revision')
        skip.add_argument('-f', '--filename',
                          help="skip only this filename",
                          action="append")

    def add_show(self):
        usage = """
    pgv show [--help]
    pgv show [-s|-w] [-f REVISION] [-t REVISION]
        """

        show = self.commands.add_parser('show', add_help=False,
                                        help="show revisions", usage=usage)
        show.add_argument('--help', action="help")
        show.add_argument('-s', '--skipped', action="store_true")
        show.add_argument('-w', '--with-skipped', action="store_true")
        self.add_version(show)

    def parse(self, args=None):
        return self.parser.parse_args(args=args)
