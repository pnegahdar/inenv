from click.testing import CliRunner

from inenv.cli import print_version, autojump
from inenv.inenv import autojump_enabled
from inenv.version import __version__


class TestCli(object):
    def setup_method(self):
        self.runner = CliRunner()

    def invoke(self, command, args=None):
        if args is None:
            args = []
        result = self.runner.invoke(command, args)
        assert result.exit_code == 0
        return result

    def test_print_version(self):
        result = self.invoke(print_version)
        assert __version__ in result.output

    def test_autojump(self):
        for _ in range(2):  # cycle through both states!
            autojump_was_enabled = autojump_enabled()
            result = self.invoke(autojump)
            if autojump_was_enabled:
                assert 'disabled' in result.output
            else:
                assert 'enabled' in result.output
            assert autojump_was_enabled != autojump_enabled()
