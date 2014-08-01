import os


class Tracker:
    schema = "pgv"

    def __init__(self, connection):
        self.connection = connection

    def _run(self, filename):
        with self.connection.cursor() as cursor:
            cursor.callproc("%s.run" % self.schema, (filename,))
            return cursor.fetchone()[0]

    def _error(self, run_id, message):
        with self.connection.cursor() as cursor:
            cursor.callproc("%s.error" % self.schema, (run_id, message))

    def _success(self, script_id):
        with self.connection.cursor() as cursor:
            cursor.callproc("%s.success" % self.schema, (script_id,))

    def _commit(self, revision):
        with self.connection.cursor() as cursor:
            cursor.callproc("%s.commit" % self.schema, (revision,))

    def is_installed(self, revision):
        with self.connection.cursor() as cursor:
            cursor.callproc("%s.is_installed" % self.schema, (revision,))
            result = cursor.fetchone()[0]
            return result is not None

    def script(self, filename):
        this = self

        class ScriptTracker:
            def __enter__(self):
                self.run_id = this._run(filename)

            def __exit__(self, type, value, tb):
                if type is not None:
                    this._error(self.run_id, value)
                    return False
                else:
                    this._success(self.run_id)
                    return True

        return ScriptTracker()

    def revision(self, revision, **kwargs):
        this = self

        class RevisionTracker:
            def __enter__(self):
                pass

            def __exit__(self, type, value, tb):
                if type is None:
                    this._commit(revision)
                    return True
                return False

        return RevisionTracker()

    def get_revision(self):
        with self.connection.cursor() as cursor:
            cursor.callproc("%s.revision" % self.schema)
            return cursor.fetchone()[0]
