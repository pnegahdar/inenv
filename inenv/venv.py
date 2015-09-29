import hashlib
import json
import os
import shutil
import subprocess
import sys

from pip import parseopts
from pip.commands.install import InstallCommand
from virtualenv import create_environment
from virtualenv import path_locations


def file_md5(path):
    return hashlib.md5(open(path, 'rb').read()).hexdigest()

class VirtualEnv(object):
    execfile_name = 'activate_this.py'

    def __init__(self, venv_name, venv_dirs):
        self.venv_name = venv_name
        self.venv_dirs = venv_dirs
        self.old_path = os.environ.get('PATH', '')
        self.sys_prefix = sys.prefix
        self.sys_path = sys.path

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
        with open(self.cache_file, 'w+') as cache_file:
            json.dump(data, cache_file)

    def load_cache_file(self):
        if not os.path.isfile(self.cache_file):
            return {}
        with open(self.cache_file) as cache_file:
            return json.load(cache_file)

    def create(self):
        create_environment(self.path)

    @property
    def exists(self):
        return os.path.isfile(self.execfile_path)

    def create_if_dne(self):
        if not self.exists:
            self.create()

    def delete(self):
        shutil.rmtree(self.path)

    def install_requirements_file(self, path_to_file):
        cmd, args = parseopts(['install', '-r', path_to_file])
        InstallCommand().main(args)

    def install_requirements_file_with_cache(self, path_to_file):
        cache_contents = self.load_cache_file()
        file_cache = cache_contents.get('file_cache', {})
        cached_md5 = file_cache.get(path_to_file)
        calculated_md5 = file_md5(path_to_file)
        if cached_md5 and cached_md5 == calculated_md5:
            return
        else:
            self.install_requirements_file(path_to_file)
            file_cache[path_to_file] = calculated_md5
            cache_contents['file_cache'] = file_cache
            self.save_cache_file(cache_contents)

    def install_deps(self, deps):
        cmd, args = parseopts(['install'] + list(deps))
        InstallCommand().main(args)

    def install_deps_with_cache(self, deps):
        cache_contents = self.load_cache_file()
        cached_deps = cache_contents.get('dep_cache', {})
        deps_to_install = [dep for dep in list(deps) if not cached_deps.get(dep)]
        if deps_to_install:
            self.install_deps(deps_to_install)
        for dep in deps_to_install:
            cached_deps[dep] = True
            cache_contents['dep_cache'] = cached_deps
            self.save_cache_file(cache_contents)

    @property
    def activate_shell_file(self):
        return self.content_path(self.bin_dir, 'activate')

    def activate(self):
        if not self.exists:
            self.create()
        execfile(self.execfile_path, dict(__file__=self.execfile_path))

    def deactivate(self, sys_path=None, sys_prefix=None, old_path=None):
        sys.path = sys_path or self.sys_path
        sys.prefix = sys_prefix or self.sys_prefix
        os.environ['PATH'] = old_path or self.old_path

    def __enter__(self):
        self.activate()

    def __exit__(self, *exc_info):
        self.deactivate()

    def run(self, args, exit=False, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr):
        with self:
            process = subprocess.Popen(args, stdin=stdin, stdout=stdout, stderr=stderr)
            exit_code = process.wait()
        if exit:
            sys.exit(exit_code)
        return exit_code

