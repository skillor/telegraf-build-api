import os
import stat
import shutil


def rm_on_error(func, path, exc):
    if os.path.exists(path):
        os.chmod(path, stat.S_IWRITE)
        func(path)


def rm_dir(directory: str):
    shutil.rmtree(directory, ignore_errors=False, onerror=rm_on_error)
