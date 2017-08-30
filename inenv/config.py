import os

from schematics.models import Model
from schematics.types.base import StringType
from schematics.types.compound import ListType, ModelType, DictType

# List of venv names that aren't allowed.
protected_venv_names = []

class Config(Model):
    venvs = DictType(ModelType(VenvConfig), default=list)

class Python(Model):
    python = StringType(default='python', required=True)
    """The python type to use. e.g. python3.6"""

    deps = ListType(StringType)
    """Dependencies e.g. 'requirements.txt' """


class VenvConfig(Model):
    python = ModelType(Python, required=False, default=None)
    """The python configuration and dependencies for this venv"""

    env = DictType(StringType, default=None)
    """The environment variables for this venv."""


