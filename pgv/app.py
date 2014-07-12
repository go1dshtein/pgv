import os
import logging
import pgv.utils

logger = logging.getLogger(__file__)


class Application:
    def __init__(self, config, options):
        self.config = config
        self.options = options

    def do_init(self):
        import pgv.initializer
        initializer = pgv.initializer.Initializer(
            pgv.utils.get_connection_string(self.options))
        initializer.initialize(self.options.overwrite)

    def do_make(self):
        import pgv.builder
        builder = pgv.builder.Builder(self.config)
        package = builder.make(from_rev=self.options.from_rev,
                               to_rev=self.options.to_rev,
                               format=self.options.format)
        path = self.options.output
        if path is None:
            path = self.config.package.path
        package.save(path)

    def do_install(self):
        import pgv.installer
        import pgv.package
        installer = pgv.installer.Installer(
            pgv.utils.get_connection_string(self.options),
            pgv.utils.get_isolation_level(
                self.config.database.isolation_level))
        package = pgv.package.Package(self.config.package.format)
        path = self.options.input
        if path is None:
            path = self.config.package.path
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
