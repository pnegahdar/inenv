import ConfigParser
import abc
import hashlib
import json

import os
from atomicwrites import atomic_write


class AbstractProvider(object):
    __metaclass__ = abc.ABCMeta

    def activation_shell_lines(self, config, config_section):
        raise NotImplementedError

    def deactivation_shell_lines(self):
        raise NotImplementedError

    def destroy_state(self):
        raise NotImplementedError


class BaseProvider(AbstractProvider):
    def __init__(self, manager, config, config_section, inenv_name):
        """
        
        :type manager: inenv.inenv.InenvManager
        :param config: ConfigParser.Section
        :param config_section: 
        """
        self.manager = manager
        self.config = config
        self.inenv_name = inenv_name
        self.config_section = config_section

    def get_section_param(self, param, default=None):
        try:
            return self.manager.parser.get(self.config_section, param).strip()
        except ConfigParser.NoOptionError:
            return default

    def get_storage_path(self, *args):
        # Prefixing with venv_ so there is no clash old versions of inenv
        return self.manager.get_storage_path("venv_{}".format(self.inenv_name), *args)

    @property
    def cache_file(self):
        return self.get_storage_path('inenv.cache')

    def save_cache_file(self, data):
        with atomic_write(self.cache_file, overwrite=True) as cache_file:
            json.dump(data, cache_file)

    def load_cache_file(self):
        if not os.path.isfile(self.cache_file):
            return {}
        with open(self.cache_file) as cache_file:
            return json.load(cache_file)

    def file_md5(self, path):
        return hashlib.md5(open(path, 'rb').read()).hexdigest()
