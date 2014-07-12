import os
import psycopg2
import pgv.installer
import logging

logger = logging.getLogger(__name__)


class Initializer:
    schema = pgv.installer.Installer.schema
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
