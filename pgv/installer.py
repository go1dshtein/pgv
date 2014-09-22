import os
import psycopg2
import logging
from itertools import chain
from pgv.package import Package
from pgv.tracker import Tracker
import pgv.loader
from pgv.utils.exceptions import PGVIsNotInitialized
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT as AUTOCOMMIT

logger = logging.getLogger(__name__)


class Installer:
    events = type("E", (object,), Package.events)

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

        self.tracker = Tracker(metaconn)
        if not self.tracker.is_initialized():
            raise PGVIsNotInitialized()

    def _run_scripts(self, package, revision, event, **kwargs):
        kwargs["revision"] = revision
        dirname = os.path.join(package.tmpdir, revision)
        loader = pgv.loader.Loader(dirname)
        for filename in package.scripts(revision, event):
            script = loader.load(filename)
            with self.connection.cursor() as cursor:
                with self.tracker.script(filename):
                    logger.info("    run %s", filename)
                    cursor.execute(script, kwargs)

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
                    with self.schema(package, revision, schema):
                        for filename in package.schema_files(revision, schema):
                            logger.info("    script %s", filename)
                            script = loader.load(filename)
                            with self.script(package, revision, schema,
                                             filename):
                                with self.tracker.script(filename):
                                    with self.connection.cursor() as c:
                                        c.execute(script)

            if not self.connection.autocommit:
                self.connection.commit()

    def revision(self, package, revision):
        this = self
        schemas = package.schemas(revision)
        files = list(chain(
            *[package.schema_files(revision, x) for x in schemas]))
        scripts = list(chain(
            *[package.scripts(revision, x) for x in Package.events]))

        class RevisionInstaller:
            def __enter__(self):
                this._run_scripts(package, revision, this.events.start)

            def __exit__(self, type, value, tb):
                this._run_scripts(package, revision, this.events.stop)
                if type is None:
                    this.tracker.commit(
                        revision,
                        schemas=schemas,
                        files=files,
                        scripts=scripts)
                return type is None

        return RevisionInstaller()

    def schema(self, package, revision, schema):
        this = self

        class SchemaInstaller:
            def __enter__(self):
                this._run_scripts(package, revision, this.events.pre,
                                  schema=schema)

            def __exit__(self, type, value, tb):
                this._run_scripts(package, revision, this.events.post,
                                  schema=schema)
                return type is None

        return SchemaInstaller()

    def script(self, package, revision, schema, filename):
        this = self

        class ScriptInstaller:
            def __enter__(self):
                pass

            def __exit__(self, type, value, tb):
                if type is None:
                    this._run_scripts(package, revision, this.events.success,
                                      schema=schema, filename=filename)
                else:
                    this._run_scripts(package, revision, this.events.error,
                                      schema=schema, filename=filename)
                return type is None

        return ScriptInstaller()
