import os
import shutil
import tarfile
import logging

logger = logging.getLogger(__name__)


def clean(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    if os.path.exists(path):
        os.remove(path)


class TarFormat:
    def __init__(self, mode):
        self.mode = mode

    def save(self, src, path):
        clean(path)
        directory = os.path.dirname(path)
        if not os.path.isdir(directory):
            os.makedirs(directory)
        archive = tarfile.open(path, mode='w|' + self.mode)
        for file in os.listdir(src):
            archive.add(os.path.join(src, file), arcname=file)
        archive.close()

    def load(self, path, dst):
        archive = tarfile.open(path, mode='r|' + self.mode)
        archive.extractall(dst)


class DirectoryFormat:
    def save(self, src, path):
        clean(path)
        shutil.copytree(src, path)

    def load(self, path, dst):
        clean(dst)
        shutil.copytree(path, dst)


def get(format):
    if format == "tar":
        return TarFormat("")
    elif format == "tar.gz":
        return TarFormat("gz")
    elif format == "tar.bz2":
        return TarFormat("bz2")
    elif format == "directory":
        return DirectoryFormat()
    else:
        raise Exception("Unknown format: %s", format)
