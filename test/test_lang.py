import pytest

from cacti.runtime import *
from cacti.lang import *
from cacti.builtin import make_object, make_integer, make_string
from cacti.exceptions import SymbolError

@pytest.mark.usefixtures('set_up_env')
class TestObjectDefinition:
    def test_var_not_accessible_outside_object(self):
        obj = make_object()
        obj.add_var('x', make_integer(123))
        with pytest.raises(SymbolError):
            obj['x']
    
    def test_var_accessible_within_object(self):
        obj = make_object()
        obj.add_var('x', make_integer(123))
        call_env = CallEnv(obj, 'some_method')
        push_call_env(call_env)
        assert obj['x'].primitive == 123
        
    def test_calls_subclass_method(self):
        def super_some_method():
            return make_string("SUPER")
        super_callable = Callable(super_some_method)
        super_method_def = MethodDefinition('some_method', super_callable)
        super_obj = make_object()
        super_obj.add_method(super_method_def)
        
        def subclass_some_method():
            return make_string("SUBCLASS")
        subclass_callable = Callable(subclass_some_method)
        subclass_method_def = MethodDefinition('some_method', subclass_callable)
        subclass_obj = make_object()
        subclass_obj.add_method(subclass_method_def)
        
        subclass_obj.set_superobj(super_obj)
        
        assert subclass_obj['some_method'].hook_table['()']().primitive == "SUBCLASS"
    
    def test_calls_superclass_method(self):
        def super_some_method():
            return make_string("SUPER")
        super_callable = Callable(super_some_method)
        super_method_def = MethodDefinition('some_method', super_callable)
        super_obj = make_object()
        super_obj.add_method(super_method_def)
        
        def subclass_some_method():
            return peek_call_env().symbol_stack['super']['some_method'].hook_table['()']()
        subclass_callable = Callable(subclass_some_method)
        subclass_method_def = MethodDefinition('some_method', subclass_callable)
        subclass_obj = make_object()
        subclass_obj.add_method(subclass_method_def)
        
        subclass_obj.set_superobj(super_obj)
        
        assert subclass_obj['some_method'].hook_table['()']().primitive == "SUPER"
        