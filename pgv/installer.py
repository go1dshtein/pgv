import os
import psycopg2
import logging
import pgv.package
import pgv.tracker
import pgv.loader
from pgv.utils.exceptions import PGVIsNotInitialized
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT as AUTOCOMMIT

logger = logging.getLogger(__name__)


class Installer:
    events = type("E", (object,), pgv.package.Package.events)

    def __init__(self, constring, isolation_level=None):
        if isolation_level is None:
            isolation_level = AUTOCOMMIT

        self.connection = psycopg2.connect(constring)
        self.connection.set_isolation_level(isolation_level)
        if isolation_level != AUTOCOMMIT:
            metaconn = psycopg2.connect(constring)
            metaconn.set_isolation_level(AUTOCOMMIT)
        else:
            metaconn = self.connection

        self.tracker = pgv.tracker.Tracker(metaconn)
        if not self.tracker.is_initialized():
            raise PGVIsNotInitialized()

    def _run_scripts(self, package, revision, event):
        dirname = os.path.join(package.tmpdir, revision)
        loader = pgv.loader.Loader(dirname)
        for filename in package.scripts(revision, event):
            script = loader.load(filename)
            with self.connection.cursor() as cursor:
                with self.tracker.script(filename):
                    logger.info("    run %s", filename)
                    cursor.execute(script)

    def install(self, package):
        for revision in package.revlist:
            if self.tracker.is_installed(revision):
                logger.debug("revision %s is installed already", revision)
                continue

            logger.info("installing revision %s", revision)
            with self.revision(package, revision):
                directory = os.path.join(package.tmpdir, revision)
                loader = pgv.loader.Loader(directory)
                for schema in package.schemas(revision):
                    logger.info("  schema %s", schema)
                    with self.schema(package, revision):
                        for filename in package.schema_files(revision, schema):
                            logger.info("    script %s", filename)
                            script = loader.load(filename)
                            with self.script(package, revision):
                                with self.tracker.script(filename):
                                    with self.connection.cursor() as c:
                                        c.execute(script)

            if not self.connection.autocommit:
                self.connection.commit()

    def revision(self, package, revision):
        this = self

        class RevisionInstaller:
            def __enter__(self):
                this._run_scripts(package, revision, this.events.start)

            def __exit__(self, type, value, tb):
                this._run_scripts(package, revision, this.events.stop)
                if type is None:
                    this.tracker.commit(revision)
                return type is None

        return RevisionInstaller()

    def schema(self, package, revision):
        this = self

        class SchemaInstaller:
            def __enter__(self):
                this._run_scripts(package, revision, this.events.pre)

            def __exit__(self, type, value, tb):
                this._run_scripts(package, revision, this.events.post)
                return type is None

        return SchemaInstaller()

    def script(self, package, revision):
        this = self

        class ScriptInstaller:
            def __enter__(self):
                pass

            def __exit__(self, type, value, tb):
                if type is None:
                    this._run_scripts(package, revision, this.events.success)
                else:
                    this._run_scripts(package, revision, this.events.error)
                return type is None

        return ScriptInstaller()
