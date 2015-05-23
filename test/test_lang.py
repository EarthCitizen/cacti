import pytest

from cacti.lang import *
from cacti.builtin import make_object, make_integer

from util import set_up_env

@pytest.mark.usefixtures('set_up_env')
class TestObjectDefinition:
    def test_var_only_accessible_within_object(self):
        object = make_object()
        object.add_var('x', make_integer(123))
        object['x']
        