import os
import logging
import pgv.utils

logger = logging.getLogger(__file__)


class Application:
    def __init__(self, config, options):
        self.config = config
        self.options = options

    def do_initdb(self):
        import pgv.initializer
        connection = pgv.utils.get_connection_string(self.options)
        initializer = pgv.initializer.Initializer(connection)
        initializer.initialize_schema(self.options.overwrite)

    def do_init(self):
        import pgv.initializer
        initializer = pgv.initializer.Initializer()
        initializer.initialize_repo(self.options.prefix)

    def do_collect(self):
        import pgv.builder
        builder = pgv.builder.Builder(self.config)
        package = builder.make(from_rev=self.options.from_rev,
                               to_rev=self.options.to_rev,
                               format=self.options.format)
        path = self.options.output
        if path is None:
            path = self.config.package.path
        package.save(path)

    def do_push(self):
        import pgv.installer
        import pgv.package

        if self.options.collect:
            import pgv.builder
            builder = pgv.builder.Builder(self.config)
            package = builder.make(format=self.options.format)
        else:
            package = pgv.package.Package(self.config.package.format)

        installer = pgv.installer.Installer(
            pgv.utils.get_connection_string(self.options),
            pgv.utils.get_isolation_level(
                self.config.database.isolation_level))
        path = self.options.input
        if path is None:
            path = self.config.package.path
        if self.options.collect:
            package.save(path)
        package.load(path)
        installer.install(package)

    def do_skip(self):
        import pgv.skiplist
        skiplist = pgv.skiplist.SkipList(self.config)
        skiplist.add(self.options.revision, self.options.filename)

    def do_show(self):
        import pgv.viewer
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
