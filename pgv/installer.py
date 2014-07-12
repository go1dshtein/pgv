import os
import psycopg2
import logging
import pgv.package

logger = logging.getLogger(__name__)


class Installer:
    schema = "pgv"
    events = type("E", (object,), pgv.package.Package.events)

    def __init__(self, constring, isolation_level=None):
        logger.debug("connection string: %s", constring)
        if isolation_level is None:
            isolation_level = psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT
        logger.debug("isolation level: %s", isolation_level)
        self.connection = psycopg2.connect(constring)
        self.connection.set_isolation_level(isolation_level)
        if isolation_level != psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT:
            self.metaconn = psycopg2.connect(constring)
            self.metaconn.set_isolation_level(
                psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        else:
            self.metaconn = self.connection

    def _get_text(self, filename):
        with open(filename) as h:
            return h.read()

    def _meta_run(self, filename):
        with self.metaconn.cursor() as cursor:
            cursor.callproc("%s.run" % self.schema, (filename,))
            return cursor.fetchone()[0]

    def _meta_error(self, script_id, message):
        with self.metaconn.cursor() as cursor:
            cursor.callproc("%s.error" % self.schema, (script_id, message))

    def _meta_success(self, script_id):
        with self.metaconn.cursor() as cursor:
            cursor.callproc("%s.success" % self.schema, (script_id,))

    def _meta_commit(self, revision):
        with self.metaconn.cursor() as cursor:
            cursor.callproc("%s.commit" % self.schema, (revision,))

    def _meta_installed(self, revision):
        with self.metaconn.cursor() as cursor:
            cursor.callproc("%s.is_installed" % self.schema, (revision,))
            result = cursor.fetchone()[0]
            return result is not None

    def _run_scripts(self, package, revision, event):
        with self.connection.cursor() as cursor:
            for filename in package.scripts(revision, event):
                script = self._get_text(filename)
                script_id = self._meta_run(filename)
                try:
                    logger.debug("run script `%s' on event '%s': \n%s",
                                 filename, event, script)
                    cursor.execute(script)
                    logger.debug("status: \n%s", cursor.statusmessage)
                except Exception, e:
                    self._meta_error(script_id, repr(e))
                    raise
                else:
                    self._meta_success(script_id)

    def _run_schemas(self, package, revision):
        with self.connection.cursor() as cursor:
            for schema in package.schemas(revision):
                logger.info("  installing schema %s", schema)
                try:
                    self._run_scripts(package, revision, self.events.pre)
                    for filename in package.schema_files(revision, schema):
                        try:
                            script = self._get_text(filename)
                            logger.debug("run schema script `%s': \n%s",
                                         filename, script)
                            cursor.execute(script)
                            logger.debug("status: \n%s", cursor.statusmessage)
                        except:
                            self._run_scripts(package, revision,
                                              self.events.error)
                            raise
                        else:
                            self._run_scripts(package, revision,
                                              self.events.success)
                except:
                    self._run_scripts(package, revision, self.events.post)
                    raise
                else:
                    self._run_scripts(package, revision, self.events.post)
                    logger.info("  done")

    def install(self, package):
        for revision in package.revlist:
            if self._meta_installed(revision):
                logger.debug("revision %s is installed already", revision)
                continue
            logger.info("installing revision %s", revision)
            try:
                self._run_scripts(package, revision, self.events.start)
                self._run_schemas(package, revision)
            except:
                self._run_scripts(package, revision, self.events.stop)
                raise
            else:
                self._run_scripts(package, revision, self.events.stop)
                if not self.connection.autocommit:
                    self.connection.commit()
                self._meta_commit(revision)
                logger.info("done\n")


