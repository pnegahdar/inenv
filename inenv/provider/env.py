from inenv.inenv import InenvException
from inenv.provider.abstract import AbstractProvider


class EnvProvider(AbstractProvider):
    ENV_VAR_DELIMITER = "="

    def on_hash_change(self):
        # Nothing to do
        pass

    def parse_section(self):
        env_config = self.get_section_param('env', default={})
        env = {}
        if not env_config:
            return {'env': env}
        try:
            # Split envvar from A=B list
            env = dict([each.split(self.ENV_VAR_DELIMITER) for each in env_config.replace(',', '').split()])
            # Correct relative paths
            for k, v in env.items():
                if v.startswith(self.manager.FILE_PREFIX) or v.startswith(self.manager.DIR_PREFIX):
                    env[k] = self.manager.full_relative_path(
                        v.replace(self.manager.FILE_PREFIX, '').replace(self.manager.DIR_PREFIX, ''))
        except ValueError:
            raise InenvException(
                "Unable to parse ini file env section. Use space separated K{}V pairs.".format(
                    self.ENV_VAR_DELIMITER))
        return {'env': env}

    def activation_shell_contents(self, config, config_section):
        activate_template = "export _OLD_{key}=${key} {key}={new_value}"
        if not self.parsed_section['env']:
            return None
        else:
            lines = [activate_template.format(key=k, new_value=v) for k, v in self.parsed_section['env'].items()]
            return '\n'.join(lines)

    def deactivation_shell_contents(self):
        # TODO: check if last key was set
        deactivate_template = "unset {key}; export {key}=\"$_OLD_{key}\"; unset _OLD_{key}"
        if not self.parsed_section['env']:
            return None
        else:
            lines = [deactivate_template.format(key=k) for k, v in self.parsed_section['env'].items()]
            return '\n'.join(lines)
