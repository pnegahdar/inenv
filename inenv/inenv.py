import ConfigParser

import os
from venv import VirtualEnv
from version import __version__

INI_NAME = 'inenv.ini'
VENV_DIR_NAME = '.inenv'
RECURSION_LIMIT = 100
EVAL_EXIT_CODE = 200


class InenvException(Exception):
    pass


INENV_ENV_VAR = 'INENV_VERSION'
EXTRA_SOURCE_NAME = 'inenv_extra.sh'
ACTIVATE_TEMPLATE_NAME = 'inenv.sh'
ACTIVATE_TEMPLATE = '''export {env_var}={version}
function inenv() {{
    inenv_helper $@
    rc=$?
    if [[ $rc == \'{eval_exit_code}\' ]]; then
        `cat $(inenv_helper extra_source)`
    fi
}}
'''.format(env_var=INENV_ENV_VAR, version=__version__, eval_exit_code=EVAL_EXIT_CODE)


class InenvManager(object):
    def __init__(self, ini_path=None, ini_name=INI_NAME, venv_dir_name=VENV_DIR_NAME,
                 no_setup=False):
        self.ini_name = ini_name
        self.ini_path = ini_path or self.get_closest_ini()
        self.venv_dir_name = venv_dir_name
        self.parser = ConfigParser.ConfigParser()
        self.registered_venvs = self.parse_ini()
        if not no_setup:
            self.setup_activator()

    def get_closest_ini(self):
        directory = os.path.realpath(os.path.curdir)
        x = RECURSION_LIMIT
        while x > 0:
            ini_path = os.path.join(directory, self.ini_name)
            if not os.access(directory, os.W_OK):
                raise InenvException(
                    "Lost permissions walkign up to {}. Unable to find {}".format(directory,
                                                                                  self.ini_name))
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

    def parse_ini(self):
        venv_sections = {}
        with open(self.ini_path) as parse_file:
            try:
                self.parser.readfp(parse_file)
            except ConfigParser.ParsingError:
                raise InenvException("Unable to parse ini file {}".format(self.ini_path))
        for venv_name in self.parser.sections():
            data = self.parse_section(venv_name)
            venv_sections[venv_name] = data
        return venv_sections

    def parse_section(self, section):
        data = {'deps': []}
        try:
            deps = [dep for dep in self.parser.get(section, 'deps').replace(',', '').split()]
            data['deps'] += deps
        except ConfigParser.NoOptionError:
            pass
        return data

    @property
    def venv_dir(self):
        dir = os.path.join(os.path.dirname(self.ini_path), ".inenv/")
        if not os.path.exists(dir):
            os.makedirs(dir)
        return dir

    def _fix_venv_name_input(self, venv_name):
        if venv_name in self.registered_venvs:
            return venv_name
        is_prefix_of = [key for key in self.registered_venvs.keys() if key.startswith('venv_name')]
        if is_prefix_of and len(is_prefix_of) == 1:
            return is_prefix_of[0]
        return venv_name

    def get_venv(self, venv_name):
        venv_name = self._fix_venv_name_input(venv_name)
        if venv_name not in self.registered_venvs:
            raise InenvException("Venv {} not in config file {}".format(venv_name, self.ini_path))
        return VirtualEnv(venv_name, self.venv_dir)

    def _full_relative_path(self, path):
        if os.path.isabs(path):
            return path
        return os.path.normpath(os.path.join(os.path.dirname(self.ini_path), path))

    def install_deps(self, virtualenv):
        """

        :param virtualenv:
        :type virtualenv: VirtualEnv
        :return:
        """
        config = self.registered_venvs[virtualenv.venv_name]
        inline_deps = []
        for dep in config['deps']:
            if dep.startswith('file:'):
                dep = self._full_relative_path(dep.split('file:')[1])
                virtualenv.install_requirements_file_with_cache(dep)
            else:
                inline_deps.append(dep)
        if inline_deps:
            virtualenv.install_deps_with_cache(inline_deps)

    def get_prepped_venv(self, venv_name):
        venv = self.get_venv(venv_name)
        venv.create_if_dne()
        self.install_deps(venv)
        return venv

    @property
    def activate_file(self):
        return os.path.join(self.venv_dir, ACTIVATE_TEMPLATE_NAME)

    @property
    def extra_source_file(self):
        return os.path.join(self.venv_dir, EXTRA_SOURCE_NAME)

    def setup_activator(self, only_if_dne=False):
        exists = os.path.isfile(self.activate_file)
        if not only_if_dne or not exists:
            with open(self.activate_file, 'w+') as writefile:
                writefile.write(ACTIVATE_TEMPLATE)

    def clear_extra_source_file(self):
        open(self.extra_source_file, 'w+').close()

    def write_extra_source_file(self, contents):
        with open(self.extra_source_file, 'w+') as writefile:
            writefile.write(contents)

