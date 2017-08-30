from inenv.provider.abstract import BaseProvider
from inenv.venv import VirtualEnv


class PythonVenvProvider(BaseProvider):

    def __init__(self, *args, **kwargs):
        super(self).__init__(*args, **kwargs)
        self.venv_helper = VirtualEnv(self.inenv_name, self.get_storage_path())

    def parse_section(self):
        deps = self.get_section_param('deps', [])
        if deps:
            deps = deps.replace(',', ' ').split()
        return {
            'python': self.get_section_param('python', 'python'),
            'deps': deps
        }

    def activation_shell_lines(self, config, config_section):
        lines = []
        if self.should_install:
            lines.append(['pip', 'install', '-r', 'file.txt'])

    def venv_dir(self):
        pass

    def _install_deps_lines(self, skip_cached=True):
        """
        :type virtualenv: VirtualEnv
        """
        cache_contents = self.load_cache_file()
        file_cache = cache_contents.get('python_file_dep_cache', {})
        cached_deps = cache_contents.get('python_dep_cache', {})
        commands = []
        for i, dep in enumerate(self.parsed_section['deps']):
            if dep.startswith(self.manager.FILE_PREFIX):
                path_to_file = self.manager.full_relative_path(dep.replace(self.manager.FILE_PREFIX, ''))
                cached_md5 = file_cache.get(path_to_file)
                calculated_md5 = self.file_md5(path_to_file)
                if cached_md5 and cached_md5 == calculated_md5 and skip_cached:
                    continue
                commands.append('pip install -r {}'.format(path_to_file))

            else:
                if cached_deps.get(dep) and skip_cached:
                    continue
                commands.append(['pip install {}'.format(dep)])

    def _activate_venv_lines(self):
        pass

    def _initialize_venv_lines(self):
        pass
