import os
import logging
import pgv.installer
import pgv.builder
import pgv.initializer
import pgv.package
import pgv.skiplist
import pgv.viewer
import pgv.utils.misc

logger = logging.getLogger(__file__)


class Application:
    def __init__(self, config, options):
        self.config = config
        self.options = options

    def do_initdb(self):
        connection = pgv.utils.misc.get_connection_string(self.options)
        initializer = pgv.initializer.Initializer(connection)
        if self.options.revision:
            builder = pgv.builder.Builder(self.config)
            revisions = map(
                lambda x: x[0].hash(),
                builder.get_revisions(to_rev=self.options.revision))
        initializer.initialize_schema(self.options.overwrite, revisions)

    def do_init(self):
        initializer = pgv.initializer.Initializer()
        initializer.initialize_repo(self.options.prefix)

    def do_collect(self):
        if self.options.dbname and not self.options.from_rev:
            connection = pgv.utils.misc.get_connection_string(self.options)
            installer = pgv.installer.Installer(connection)
            from_rev = installer.get_revision()
        else:
            from_rev = self.options.from_rev

        builder = pgv.builder.Builder(self.config)
        package = builder.make(from_rev=from_rev,
                               to_rev=self.options.to_rev,
                               format=self.options.format)
        path = self.options.output
        if path is None:
            path = self.config.package.path
        package.save(path)

    def do_push(self):
        installer = pgv.installer.Installer(
            pgv.utils.misc.get_connection_string(self.options),
            pgv.utils.misc.get_isolation_level(
                self.config.database.isolation_level))

        if self.options.collect:
            builder = pgv.builder.Builder(self.config)
            from_rev = installer.get_revision()
            package = builder.make(from_rev=from_rev,
                                   format=self.options.format)
        else:
            package = pgv.package.Package(self.config.package.format)

        path = self.options.input
        if path is None:
            path = self.config.package.path
        if self.options.collect:
            package.save(path)
        package.load(path)
        installer.install(package)

    def do_skip(self):
        vcs = pgv.vcs.get(**self.config.vcs.__dict__)
        skiplist = pgv.skiplist.SkipList(vcs, self.config.config.dirname)
        skiplist.add(self.options.revision, self.options.filename)

    def do_show(self):
        viewer = pgv.viewer.Viewer(self.config)
        if self.options.skipped:
            viewer.show_skipped(self.options.to_rev)
        else:
            viewer.show(self.options.with_skipped,
                        from_rev=self.options.from_rev,
                        to_rev=self.options.to_rev)

    def run(self, command):
        action = "do_%s" % command
        if action not in dir(self):
            raise AttributeError("Unknown command: %s", command)
        getattr(self, action)()
