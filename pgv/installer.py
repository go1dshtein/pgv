import os
import psycopg2
import logging
import pgv.package

logger = logging.getLogger(__name__)


class Installer:
    schema = "pgv"

    def __init__(self, constring, isolation_level=None):
        logger.debug("connection string: %s", constring)
        if isolation_level is None:
            isolation_level = psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT
        logger.debug("isolation level: %s", isolation_level)
        self.connection = psycopg2.connect(constring)
        self.connection.set_isolation_level(isolation_level)
        self.metaconn = psycopg2.connect(constring)
        self.metaconn.set_isolation_level(
            psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

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
                    self._run_scripts(package, revision, "pre")
                    for filename in package.schema_files(revision, schema):
                        try:
                            script = self._get_text(filename)
                            logger.debug("run schema script `%s': \n%s",
                                         filename, script)
                            cursor.execute(script)
                            logger.debug("status: \n%s", cursor.statusmessage)
                        except:
                            self._run_scripts(package, revision, "error")
                            raise
                        else:
                            self._run_scripts(package, revision, "success")
                except:
                    self._run_scripts(package, revision, "post")
                    raise
                else:
                    self._run_scripts(package, revision, "post")
                    logger.info("  done")

    def install(self, package):
        for revision in package.revlist:
            if self._meta_installed(revision):
                logger.debug("revision %s is installed already", revision)
                continue
            logger.info("installing revision %s", revision)
            try:
                self._run_scripts(package, revision, "start")
                self._run_schemas(package, revision)
            except:
                self._run_scripts(package, revision, "stop")
                raise
            else:
                self._run_scripts(package, revision, "stop")
                self._meta_commit(revision)
                logger.info("done\n")


class Initializer:
    schema = Installer.schema
    init_script = os.path.join(os.path.dirname(__file__), 'init', 'init.sql')

    def __init__(self, constring):
        logger.debug("connection string: %s", constring)
        self.connection = psycopg2.connect(constring)

    def is_installed(self):
        query = """
            select count(*)
              from pg_catalog.pg_namespace n
             where n.nspname = %s"""
        with self.connection.cursor() as cursor:
            cursor.execute(query, (self.schema,))
            count = cursor.fetchone()[0]
        return count > 0

    def initialize(self, overwrite=False):
        if self.is_installed():
            logger.warning("%s schema is installed already", self.schema)
            if not overwrite:
                return
            logger.warning("overwriting schema %s ...", self.schema)

        with open(self.init_script) as h:
            script = h.read()

        with self.connection.cursor() as cursor:
            logger.debug(script)
            cursor.execute(script)
        self.connection.commit()