import os
import psycopg2
import logging
import yaml
import pgv.installer
import pgv.package
import pgv.utils.misc
import pgv.config
import pgv.tracker

logger = logging.getLogger(__name__)


class DatabaseInitializer:
    schema = pgv.tracker.Tracker.schema
    init_script = os.path.join(os.path.dirname(__file__), 'data', 'init.sql')

    def __init__(self, connstring):
        self.connection = psycopg2.connect(connstring)
        self.tracker = pgv.tracker.Tracker(self.connection)

    def _read_script(self):
        with open(self.init_script) as h:
            return h.read()

    def _push_script(self, script):
        with self.connection.cursor() as cursor:
            logger.debug(script)
            cursor.execute(script)

    def _mark_revisions(self, revisions):
        if not revisions:
            return
        with self.connection.cursor() as cursor:
            for revision in revisions:
                logger.warning("marking revision %s as installed",
                               revision)
                cursor.callproc("%s.commit" % self.schema, (revision,))

    def initialize(self, overwrite=False, revisions=None):
        if self.tracker.is_initialized():
            logger.info("%s schema is initialized already", self.schema)
            if not overwrite:
                return
            logger.info("overwriting schema %s ...", self.schema)

        script = self._read_script()
        self._push_script(script)
        self._mark_revisions(revisions)
        self.connection.commit()


class RepositoryInitializer:
    def _is_config(self, current):
        config = os.path.join(current, pgv.config.name)
        if not os.path.exists(config):
            config = pgv.utils.misc.search_config()
        if config:
            logger.info("repository is initialized already:")
            logger.info("  see: %s", config)
            return True
        return False

    def _create_config(self, current, prefix):
        logger.info("initializing repository")
        config = os.path.join(current, pgv.config.name)
        with open(config, "w") as h:
            h.write(yaml.dump({"vcs": {"prefix": prefix}},
                              default_flow_style=False))

    def _create_directory(self, name, dirname):
        dirname = os.path.join(dirname, name)
        if os.path.exists(dirname):
            logging.info("%s already exists, skipping ...", name)
        else:
            os.makedirs(dirname)

    def initialize(self, prefix=""):
        current = os.getcwd()
        if self._is_config(current):
            return
        self._create_config(current, prefix)
        dirname = os.path.join(current, prefix)
        self._create_directory(pgv.package.Package.schemas_dir, dirname)
        self._create_directory(pgv.package.Package.scripts_dir, dirname)
