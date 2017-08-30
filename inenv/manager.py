import os

INENV_EXT = '.inenv'

class InenvException(Exception):
    pass


class ConfigLoader(object):

    def __init__(self, enable_known_inis=False):
        pass

    def load_inis(self, inis):
        pass

    def load_closest_config(self, start_dir=None, ext=INENV_EXT):
        directory = start_dir or os.path.realpath(os.path.curdir)
        recurse_limit = 100
        while recurse_limit > 0:
            # TODO: ext
            ini_path = os.path.join(directory, INENV_EXT)
            if not os.access(directory, os.W_OK):
                raise InenvException(
                    "Lost permissions walking up to {}. Unable to find {}".format(directory,
                                                                                  INENV_EXT))
            if os.path.isfile(ini_path):
                return ini_path
            parent_dir = os.path.realpath(os.path.join(directory, '..'))
            if parent_dir == directory:
                raise InenvException(
                    "Walked all the way up to {} and was unable to find {}".format(parent_dir,
                                                                                   INENV_EXT))
            directory = parent_dir
            recurse_limit -= 1
        raise InenvException("Recursion limit exceeded unable to find inenv.ini")



class Manager(object):
    pass

    def activate(self):
        pass

    def execute(self):
        pass
