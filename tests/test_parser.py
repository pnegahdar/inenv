import os

from unittest import TestCase
from preggy import expect
from inenv.inenv import parse_ini

my_path = os.path.dirname(os.path.abspath(__file__))
test_ini_path = os.path.join(my_path, 'fixtures', 'inenv.ini')


class TestParser(TestCase):
    def test_parse_init(self):
        parsed = dict(parse_ini(test_ini_path))
        expect(parsed).to_be_like({
            'app2': {'env_stoarge': 'tests/fixtures/',
                     'deps': ['file:my/sub/dir/requirements.txt']},
            'app1': {'deps': ['scipy==1.2.1', 'file:requirements.txt']}})

        os.environ['jenkins'] = 'true'

        parsed = dict(parse_ini(test_ini_path))
        expect(parsed).to_be_like(
            {'app2': {'env_stoarge': 'tests/fixtures/', 'deps': ['pip==6.0.8']},
             'app1': {'env_stoarge': 'tests/fixtures/', 'deps': []}})

        os.environ['second'] = 'true'
        parsed = dict(parse_ini(test_ini_path))
        expect(parsed).to_be_like(
            {'app2': {'env_stoarge': 'tests/fixtures/', 'deps': ['pip==6.0.0']},
             'app1': {'env_stoarge': 'tests/fixtures/', 'deps': []}})
