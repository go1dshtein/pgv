import os
import argparse


class Parser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(add_help=False)
        self.parser.add_argument('--help', action="help")
        self.parser.add_argument('-c', '--config', metavar="CONFIG",
                                 default=None,
                                 help="main configuration file")
        self.commands = self.parser.add_subparsers(dest="command")
        self.add_init()
        self.add_initdb()
        self.add_collect()
        self.add_push()
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

    def add_package(self, parser, isoutput):
        g = parser.add_argument_group(title="optional package arguments")
        if isoutput:
            g.add_argument('-o', '--output', metavar="PATH")
        else:
            g.add_argument('-i', '--input', metavar="PATH")
        g.add_argument('-F', '--format',
                       choices=("tar", "tar.gz", "tar.bz2", "directory"))

    def add_initdb(self):
        usage = """
    pgv initdb [--help]
    pgv initdb [-o] [-r REVISION] -d DBNAME [-h HOST] [-p PORT] \
[-U USERNAME] [-w|-W]
        """

        initdb = self.commands.add_parser(
            'initdb', add_help=False, usage=usage,
            help="initializes new database for working pgv")
        initdb.add_argument('--help', action="help",
                            help="print help and exit")
        initdb.add_argument('-o', '--overwrite', action="store_true",
                            help="overwrite if schema exists in database")
        initdb.add_argument('-r', '--revision',
                            help="mark that database is updated to revision")
        self.add_connection(initdb, required=True)

    def add_init(self):
        usage = """
    pgv init [--help]
    pgv init [-p PATH]
        """
        init = self.commands.add_parser(
            'init', add_help=False, usage=usage,
            help="initializes repository in the current directory")
        init.add_argument('--help', action="help",
                          help="print help and exit")
        init.add_argument('-p', '--prefix', metavar="PATH",
                          help="relative path to schemas directory",
                          default="")

    def add_collect(self):
        usage = """
    pgv collect [--help]
    pgv collect [-f REVISION] [-t REVISION] [-o PATH] [-F FORMAT]
    pgv collect -d DBNAME [-h HOST] [-p PORT] [-U USERNAME] [-w|-W] \
[-t REVISION] [-o PATH] [-F FORMAT]
        """

        collect = self.commands.add_parser('collect', add_help=False,
                                           help="collect changes into package",
                                           usage=usage)
        collect.add_argument('--help', action="help")
        self.add_package(collect, True)
        self.add_version(collect)
        self.add_connection(collect)

    def add_push(self):
        usage = """
    pgv push [--help]
    pgv push [-c] -d DBNAME [-h HOST] [-p PORT] [-U USERNAME] [-w|-W] \
[-i PATH] [-F FORMAT]
        """

        push = self.commands.add_parser('push', add_help=False,
                                        help="applies changes to target",
                                        usage=usage)
        push.add_argument('--help', action="help",
                          help="print help and exit")
        push.add_argument('-c', '--collect', help="alias to collect && push",
                          action="store_true")
        self.add_package(push, False)
        self.add_connection(push, True)

    def add_skip(self):
        usage = """
    pgv skip [--help]
    pgv skip [[-f FILENAME],...] revision
        """

        skip = self.commands.add_parser('skip', add_help=False,
                                        help="skip changes",
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
                                        help="shows revisions", usage=usage)
        show.add_argument('--help', action="help")
        show.add_argument('-s', '--skipped', action="store_true",
                          help="shows only skipped revisions")
        show.add_argument('-w', '--with-skipped', action="store_true"
                          help="shows skipped revisions")
        self.add_version(show)


def parse(args=None):
    return Parser().parser.parse_args(args=args)
