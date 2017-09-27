import os
from inenv.inenv import InenvManager

HERE = os.path.dirname(os.path.abspath(__file__))
TEST_INI_DIR = os.path.join(HERE, 'fixtures')
TEST_INI_PATH = os.path.join(TEST_INI_DIR, 'inenv.ini')


def test_parse_init():
    inenv = InenvManager(TEST_INI_PATH, no_setup=True)
    # this might break on windows...
    app2_dir = os.path.join('my', 'sub', 'dir')
    assert inenv.registered_venvs == {
        'app2': {
            'deps': ['file:{}'.format(os.path.join(app2_dir, 'requirements.txt'))],
            'env': {},
            'hash': None,
            'python': None,
            'root': os.path.join(TEST_INI_DIR, app2_dir)
            },
        'app1': {
            'deps': ['scipy==1.2.1', 'file:requirements.txt'],
            'env': {},
            'hash': None,
            'python': None,
            'root': TEST_INI_DIR
            }
        }
