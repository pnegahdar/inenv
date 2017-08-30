import ConfigParser
import sys

import os

from venv import VirtualEnv
from version import __version__


INI_NAME = 'inenv.ini'
VENV_DIR_NAME = '.inenv'
RECURSION_LIMIT = 100
EVAL_EXIT_CODE = 200
INENV_ENV_VAR = 'INENV_VERSION'
EXTRA_SOURCE_NAME = 'inenv_extra.sh'
ACTIVATE_TEMPLATE_NAME = 'inenv.sh'
ACTIVATE_TEMPLATE = '''export {env_var}={version}
function inenv() {{
    inenv_helper $@
    rc=$?
    if [[ $rc == \'{eval_exit_code}\' ]]; then
        source $(inenv_helper extra_source)
    else
        return $rc
    fi
}}
'''.format(env_var=INENV_ENV_VAR, version=__version__, eval_exit_code=EVAL_EXIT_CODE)
INENV_CONFIG_DIR = os.path.expanduser("~/.config/inenv/")
if not os.path.isdir(INENV_CONFIG_DIR):
    os.makedirs(INENV_CONFIG_DIR)
AUTOJUMP_FILE = os.path.join(INENV_CONFIG_DIR, 'autojump')
ENV_VAR_DELIMITER = "="


class InenvManager(object):
    FILE_PREFIX = 'file:'
    DIR_PREFIX = 'dir:'

    def __init__(self, ini_path=None, ini_name=INI_NAME, venv_dir_name=VENV_DIR_NAME,
                 no_setup=False, search_start_dir=None):
        self.ini_name = ini_name
        self.ini_path = ini_path or self.find_closest_ini(search_start_dir)
        self.venv_dir_name = venv_dir_name
        self.parser = ConfigParser.ConfigParser()
        self.registered_venvs = self._parse_ini()
        if not no_setup:
            self.setup_activator()

    @staticmethod
    def find_closest_ini(start_dir=None, ini_name=INI_NAME):
        directory = start_dir or os.path.realpath(os.path.curdir)
        x = RECURSION_LIMIT
        while x > 0:
            ini_path = os.path.join(directory, ini_name)
            if not os.access(directory, os.W_OK):
                raise InenvException(
                    "Lost permissions walking up to {}. Unable to find {}".format(directory,
                                                                                  ini_name))
            if os.path.isfile(ini_path):
                return ini_path
            parent_dir = os.path.realpath(os.path.join(directory, '..'))
            if parent_dir == directory:
                raise InenvException(
                    "Walked all the way up to {} and was unable to find {}".format(parent_dir,
                                                                                   INI_NAME))
            directory = parent_dir
            x -= 1
        raise InenvException("Recursion limit exceeded unable to find inenv.ini")

    def _parse_ini(self):
        venv_sections = {}
        with open(self.ini_path) as parse_file:
            try:
                self.parser.readfp(parse_file)
            except ConfigParser.ParsingError:
                raise InenvException("Unable to parse ini file {}".format(self.ini_path))
        for venv_name in self.parser.sections():
            data = self._parse_section(venv_name)
            venv_sections[venv_name] = data
        return venv_sections

    def _parse_section(self, section):
        data = {'deps': [], 'root': '', 'env': {}, 'python': None, 'hash': None, 'node_package': None,
                'node_version': None}
        # Parse the deps
        # Parse the root
        try:
            data['root'] = self.full_relative_path(self.parser.get(section, 'root').strip())
        except ConfigParser.NoOptionError:
            # No root set, guess using requirements.txt
            for dep in data['deps']:
                if dep.startswith(FILE_PREFIX):
                    data['root'] = self.full_relative_path(
                        os.path.dirname(dep.replace(FILE_PREFIX, '')))
        if not data['root']:
            data['root'] = os.path.dirname(self.ini_path)
        data['python'] = self.get_section_param_or_none(section, 'python')
        data['hash'] = self.get_section_param_or_none(section, 'hash')
        data['node_package'] = self.get_section_param_or_none(section, 'node_package')
        data['node_version'] = self.get_section_param_or_none(section, 'node_version')

        return data

    def full_relative_path(self, path):
        if os.path.isabs(path):
            return path
        return os.path.normpath(os.path.join(os.path.dirname(self.ini_path), path))

    def guess_contents_dir(self, venv_name):
        venv = self.registered_venvs[venv_name]
        return venv['root']

    def get_envvars(self, venv_name):
        venv = self.registered_venvs[venv_name]
        return venv['env']

    @property
    def store_dir(self):
        dir = os.path.join(os.path.dirname(self.ini_path), ".inenv/")
        if not os.path.exists(dir):
            os.makedirs(dir)
        return dir

    def get_storage_path(self, *args):
        return os.path.join(self.store_dir, *args)

    def _fix_venv_name_input(self, venv_name):
        if venv_name in self.registered_venvs:
            return venv_name
        is_prefix_of = [key for key in self.registered_venvs.keys() if key.startswith('venv_name')]
        if is_prefix_of and len(is_prefix_of) == 1:
            return is_prefix_of[0]
        return venv_name

    def get_venv(self, venv_name):
        venv_name = self._fix_venv_name_input(venv_name)
        venv_info = self.registered_venvs.get(venv_name)
        if not venv_info:
            raise InenvException("Venv {} not in config file {}".format(venv_name, self.ini_path))
        return VirtualEnv(venv_name, self.store_dir, addon_env_vars=venv_info['env'], python=venv_info['python'],
                          venv_hash=venv_info['hash'])



    @property
    def activate_file(self):
        return os.path.join(self.store_dir, ACTIVATE_TEMPLATE_NAME)

    @property
    def extra_source_file(self):
        return os.path.join(self.store_dir, EXTRA_SOURCE_NAME)

    def setup_activator(self, only_if_dne=False):
        exists = os.path.isfile(self.activate_file)
        if not only_if_dne or not exists:
            with open(self.activate_file, 'w+') as writefile:
                writefile.write(ACTIVATE_TEMPLATE)

    def clear_extra_source_file(self):
        open(self.extra_source_file, 'w+').close()

    def write_extra_source_file(self, contents):
        with open(self.extra_source_file, 'a') as writefile:
            writefile.write(contents + '\n')

def autojump_enabled():
    """ Returns whehter autojump is enabled"""
    return os.path.isfile(AUTOJUMP_FILE)


def toggle_autojump():
    """Toggles Autojump"""
    if not autojump_enabled():
        with open(AUTOJUMP_FILE, 'w+') as ajfile:
            ajfile.write("enabled")
    else:
        os.remove(AUTOJUMP_FILE)
