import pytest

from cacti.runtime import *
from cacti.lang import *
from cacti.builtin import make_object, make_integer
from cacti.exceptions import SymbolError

@pytest.mark.usefixtures('set_up_env')
class TestObjectDefinition:
    def test_var_not_accessible_outside_object(self):
        object = make_object()
        object.add_var('x', make_integer(123))
        with pytest.raises(SymbolError):
            object['x']
    
    def test_var_accessible_within_object(self):
        object = make_object()
        object.add_var('x', make_integer(123))
        call_env = CallEnv(object, 'some_method')
        push_call_env(call_env)
        assert object['x'].primitive == 123
        