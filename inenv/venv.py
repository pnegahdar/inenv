import hashlib
import json
import shutil
import subprocess
import os
import copy
import signal
import sys

from atomicwrites import atomic_write
from virtualenv import path_locations


class VirtualEnv(object):
    execfile_name = 'activate_this.py'

    def __init__(self, venv_name, venv_dirs, addon_env_vars=None, python=None, venv_hash=None):
        self.venv_name = venv_name
        self.venv_dirs = venv_dirs
        self.python = python
        self.venv_hash = venv_hash


    @property
    def path(self):
        return os.path.join(self.venv_dirs, self.venv_name)

    def content_path(self, *paths):
        return os.path.join(self.path, *paths)

    @property
    def bin_dir(self):
        return path_locations(self.path)[3]

    @property
    def execfile_path(self):
        return self.content_path(self.bin_dir, self.execfile_name)

    @property
    def activate_shell_file(self):
        return self.content_path(self.bin_dir, 'activate')

    @property
    def exists(self):
        return os.path.isfile(self.execfile_path)

    def install_requirements_file(self, path_to_file, skip_cached=True, always_exit=False,
                                  exit_if_failed=True, stdin=sys.stdin, stdout=sys.stdout,
                                  stderr=sys.stderr):
        cache_contents = self.load_cache_file()
        file_cache = cache_contents.get('file_cache', {})
        cached_md5 = file_cache.get(path_to_file)
        calculated_md5 = file_md5(path_to_file)
        if cached_md5 and cached_md5 == calculated_md5 and skip_cached:
            return
        else:
            self.run(['pip', 'install', '-r', path_to_file], always_exit=always_exit,
                     exit_if_failed=exit_if_failed, stdin=stdin, stdout=stdout, stderr=stderr)
            file_cache[path_to_file] = calculated_md5
            cache_contents['file_cache'] = file_cache
            self.save_cache_file(cache_contents)

    def install_deps(self, deps, skip_cached=True, always_exit=False, exit_if_failed=True,
                     stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr):
        cache_contents = self.load_cache_file()
        cached_deps = cache_contents.get('dep_cache', {})
        deps_to_install = [dep for dep in list(deps) if not (cached_deps.get(dep) and skip_cached)]
        if deps_to_install:
            self.run(['pip', 'install'] + list(deps), always_exit=always_exit,
                     exit_if_failed=exit_if_failed, stdin=stdin, stdout=stdout, stderr=stderr)
            for dep in deps_to_install:
                cached_deps[dep] = True
                cache_contents['dep_cache'] = cached_deps
        self.save_cache_file(cache_contents)


    def run(self, args, always_exit=False, exit_if_failed=False, stdin=sys.stdin, stdout=sys.stdout,
            stderr=sys.stderr, env=None):
        self.prep()
        cmd = ['sh', '-c', ". {} && exec {}".format(self.activate_shell_file, ' '.join(args))]
        env = env or dict(self.original_os_environ.items() + self.addon_env_vars.items())
        process = None
        try:
            process = subprocess.Popen(cmd, stdin=stdin, stdout=stdout, stderr=stderr, env=env)
            process.wait()
        except KeyboardInterrupt:
            if process:
                process.send_signal(signal.SIGINT)
                exit(process.wait())
            else:
                raise
        exit_code = process.wait()
        if always_exit or (exit_if_failed and exit_code != 0):
            sys.exit(exit_code)
        return process
