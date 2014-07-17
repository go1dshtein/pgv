import os
import psycopg2
import logging
import yaml
import pgv.installer
import pgv.package
import pgv.utils

logger = logging.getLogger(__name__)


class Initializer:
    schema = pgv.installer.Installer.schema
    init_script = os.path.join(os.path.dirname(__file__), 'init', 'init.sql')

    def __init__(self, constring=None):
        if constring:
            self.repo_only = False
            logger.debug("connection string: %s", constring)
            self.connection = psycopg2.connect(constring)
        else:
            self.repo_only = True

    def is_installed(self):
        query = """
            select count(*)
              from pg_catalog.pg_namespace n
             where n.nspname = %s"""
        with self.connection.cursor() as cursor:
            cursor.execute(query, (self.schema,))
            count = cursor.fetchone()[0]
        return count > 0

    def initialize_repo(self, prefix=""):
        logger.info("initializing repository")
        current = os.getcwd()
        config = os.path.join(current, ".pgv")
        with open(config, "w") as h:
            h.write(yaml.dump({"vcs": {"prefix": prefix}},
                              default_flow_style=False))
        schemas = os.path.join(
            current, prefix, pgv.package.Package.schemas_dir)
        scripts = os.path.join(
            current, prefix, pgv.package.Package.scripts_dir)
        if os.path.exists(schemas):
            logging.warning("%s already exists, skipping ...", schemas)
        else:
            os.makedirs(schemas)
        if os.path.exists(scripts):
            logging.warning("%s already exists, skipping ...", scripts)
        else:
            os.makedirs(scripts)

    def initialize_schema(self, overwrite=False):
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

    def initialize(self, prefix="", overwriting=False):
        current = os.getcwd()
        config = os.path.join(current, ".pgv")
        if not os.path.exists(config):
            config = pgv.utils.search_config()
        if not config:
            self.initialize_repo(prefix)
        elif self.repo_only:
            logger.warning("repository is initialized already:")
            logger.warning("  see: %s", config)
        else:
            logger.debug("repository is initialized: %s", config)
        if not self.repo_only:
            self.initialize_schema(overwriting)
