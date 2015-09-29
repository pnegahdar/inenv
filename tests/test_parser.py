from unittest import TestCase

import os
from preggy import expect
from inenv.inenv import InenvManager

my_path = os.path.dirname(os.path.abspath(__file__))
test_ini_path = os.path.join(my_path, 'fixtures', 'inenv.ini')


class TestParser(TestCase):
    def test_parse_init(self):
        inenv = InenvManager(test_ini_path, no_setup=True)
        expect(inenv.registered_venvs).to_be_like({
            'app2': {'deps': ['file:my/sub/dir/requirements.txt']},
            'app1': {'deps': ['scipy==1.2.1', 'file:requirements.txt']}})

