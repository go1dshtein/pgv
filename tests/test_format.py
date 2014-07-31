import unittest
import os
import shutil
import tempfile
import pgv.format


class TestFormat(unittest.TestCase):
    def setUp(self):
        self.src = os.path.join(os.path.dirname(__file__), "data")
        self.src_files = self._get_files(self.src)

    def _get_files(self, path):
        result = []
        for root, dirnames, filenames in os.walk(path):
            for filename in filenames:
                result.append(os.path.join(root, filename))
            for dirname in dirnames:
                result.append(os.path.join(root, dirname))
        return map(lambda x: x[len(path):].lstrip('/'), result)

    def test_directory(self):
        tmpdir = tempfile.mkdtemp()
        dst = tempfile.mkdtemp()
        try:
            frmt = pgv.format.get("directory")
            self.assertEquals(frmt.__class__, pgv.format.DirectoryFormat)
            frmt.save(self.src, tmpdir)
            frmt.load(tmpdir, dst)
            self.assertEquals(self.src_files, self._get_files(dst))
        finally:
            if os.path.isdir(tmpdir):
                shutil.rmtree(tmpdir)
            if os.path.isdir(dst):
                shutil.rmtree(dst)

    def test_tar(self):
        tmp = tempfile.mkstemp()[1]
        dst = tempfile.mkdtemp()
        try:
            frmt = pgv.format.get("tar")
            self.assertEquals(frmt.__class__, pgv.format.TarFormat)
            self.assertEquals(frmt.mode, "")
            frmt.save(self.src, tmp)
            frmt.load(tmp, dst)
            self.assertEquals(self.src_files, self._get_files(dst))
        finally:
            if os.path.isfile(tmp):
                os.remove(tmp)
            if os.path.isdir(dst):
                shutil.rmtree(dst)

    def test_tar_gz(self):
        tmp = tempfile.mkstemp()[1]
        dst = tempfile.mkdtemp()
        try:
            frmt = pgv.format.get("tar.gz")
            self.assertEquals(frmt.__class__, pgv.format.TarFormat)
            self.assertEquals(frmt.mode, "gz")
            frmt.save(self.src, tmp)
            frmt.load(tmp, dst)
            self.assertEquals(self.src_files, self._get_files(dst))
        finally:
            if os.path.isfile(tmp):
                os.remove(tmp)
            if os.path.isdir(dst):
                shutil.rmtree(dst)

    def test_tar_bz2(self):
        tmp = tempfile.mkstemp()[1]
        dst = tempfile.mkdtemp()
        try:
            frmt = pgv.format.get("tar.bz2")
            self.assertEquals(frmt.__class__, pgv.format.TarFormat)
            self.assertEquals(frmt.mode, "bz2")
            frmt.save(self.src, tmp)
            frmt.load(tmp, dst)
            self.assertEquals(self.src_files, self._get_files(dst))
        finally:
            if os.path.isfile(tmp):
                os.remove(tmp)
            if os.path.isdir(dst):
                shutil.rmtree(dst)

    def test_unknown(self):
        self.assertRaises(Exception, pgv.format.get, "unknown")
