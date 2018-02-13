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


def file_md5(path):
    return hashlib.md5(open(path, 'rb').read()).hexdigest()


class VirtualEnv(object):
    execfile_name = 'activate_this.py'

    def __init__(self, venv_name, venv_dirs, addon_env_vars=None, python=None, venv_hash=None):
        self.venv_name = venv_name
        self.venv_dirs = venv_dirs
        self.sys_prefix = sys.prefix
        self.python = python
        self.sys_path = copy.copy(sys.path)
        self.original_os_environ = os.environ.copy()
        self.addon_env_vars = addon_env_vars or {}
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
    def cache_file(self):
        return self.content_path('.inenv.cache')

    def save_cache_file(self, data):
        with atomic_write(self.cache_file, overwrite=True) as cache_file:
            json.dump(data, cache_file)

    def load_cache_file(self):
        if not os.path.isfile(self.cache_file):
            return {}
        with open(self.cache_file) as cache_file:
            return json.load(cache_file)

    def create(self):
        base_args = ['-p', self.python] if self.python else []
        args = ['virtualenv'] + base_args + [self.path]
        subprocess.check_output(args)
        cache_contents = self.load_cache_file()
        cache_contents['venv_hash'] = self.venv_hash
        self.save_cache_file(cache_contents)

    @property
    def exists(self):
        return os.path.isfile(self.execfile_path)

    def create_if_dne(self):
        if not self.exists:
            self.create()

    def delete(self):
        shutil.rmtree(self.path)

    def __enter__(self):
        self.create_if_dne()

    def __exit__(self, exc_type, exc_value, traceback):
        self.delete()

    def rebuild_if_hash_changed(self):
        cache_contents = self.load_cache_file()
        if cache_contents.get('venv_hash') != self.venv_hash:
            # Reset other caches
            sys.stderr.write("Rebuilding due to hash change...\n")
            cache_contents = {'venv_hash': self.venv_hash}
            self.delete()
            self.create()
            self.save_cache_file(cache_contents)
            return True
        return False

    def prep(self):
        if not self.exists:
            self.create()
        else:
            self.rebuild_if_hash_changed()

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
            if self.venv_hash:
                cache_contents['venv_hash'] = self.venv_hash
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

    @property
    def activate_shell_file(self):
        return self.content_path(self.bin_dir, 'activate')

    def run(self, args, always_exit=False, exit_if_failed=False, stdin=sys.stdin, stdout=sys.stdout,
            stderr=sys.stderr, env=None):
        self.prep()
        cmd = ['sh', '-c', ". {} && exec {}".format(self.activate_shell_file, ' '.join(args))]
        if env is None:
            env = self.original_os_environ.copy()
            env.update(self.addon_env_vars)
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
