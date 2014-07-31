import os
import re
import logging

logger = logging.getLogger(__name__)


class Loader:
    def __init__(self, basedir):
        self.basedir = basedir
        self.ipattern = re.compile(r'^\\i\s+(.+?)\s*$', re.U | re.M)
        self.irpattern = re.compile(r'^\\ir\s+(.+?)\s*$', re.U | re.M)

    def load(self, path):
        filename = os.path.join(self.basedir, path)
        script = self._read(filename)
        script = self._preproceed(filename, script)
        return script

    def _read(self, path):
        with open(path) as h:
            return h.read()

    def _preproceed(self, path, script):
        imatch = self.ipattern.search(script)
        irmatch = self.irpattern.search(script)
        while imatch or irmatch:
            if imatch:
                script = self._preproceed_i(path, script, imatch)
            elif irmatch:
                script = self._preproceed_ir(path, script, irmatch)
            imatch = self.ipattern.search(script)
            irmatch = self.irpattern.search(script)
        return script

    def _preproceed_i(self, path, script, match):
        filename = match.group(1)
        if filename != os.path.abspath(filename):
            filename = os.path.join(self.basedir, match.group(1))
        return self._include(path, script, match, filename)

    def _preproceed_ir(self, path, script, match):
        filename = match.group(1)
        if filename != os.path.abspath(filename):
            dirname = os.path.dirname(path)
            filename = os.path.join(dirname, match.group(1))
        return self._include(path, script, match, filename)

    def _include(self, path, script, match, filename):
        if not os.path.isfile(filename):
            raise IOError("Script: %s: line: %s: file %s not found" %
                          (path, match.group(0), filename))
        return script[:match.start()] + \
            self._read(filename) + \
            script[match.end():]
