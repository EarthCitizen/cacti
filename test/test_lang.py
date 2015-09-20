import pytest

from cacti.runtime import *
from cacti.lang import *
from cacti.builtin import get_type, make_object, make_integer, make_string
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
        stack_frame = StackFrame(obj, 'some_method')
        push_stack_frame(stack_frame)
        assert obj['x'].primitive == 123
        
    def test_calls_subclass_method(self):
        def super_some_method():
            return make_string("SUPER")
        super_method_def = MethodDefinition('some_method', super_some_method)
        super_obj = make_object()
        super_obj.add_method(super_method_def)
        
        def subclass_some_method():
            return make_string("SUBCLASS")
        subclass_method_def = MethodDefinition('some_method', subclass_some_method)
        subclass_obj = make_object()
        subclass_obj.add_method(subclass_method_def)
        
        subclass_obj.set_superobj(super_obj)
        
        assert subclass_obj['some_method'].hook_table['()']().primitive == "SUBCLASS"
    
    def test_calls_superclass_method(self):
        def super_some_method():
            return make_string("SUPER")
        super_method_def = MethodDefinition('some_method', super_some_method)
        super_obj = make_object()
        super_obj.add_method(super_method_def)
        
        def subclass_some_method():
            return peek_stack_frame().symbol_stack['super']['some_method'].hook_table['()']()
        subclass_method_def = MethodDefinition('some_method', subclass_some_method)
        subclass_obj = make_object()
        subclass_obj.add_method(subclass_method_def)
        
        subclass_obj.set_superobj(super_obj)
        
        assert subclass_obj['some_method'].hook_table['()']().primitive == "SUPER"

@pytest.mark.usefixtures('set_up_env')
class TestModule:
    def test_type(self):
        m = Module('test')
        assert get_type('Module') is m.typeobj
        
    def test_type_type(self):
        m = Module('test')
        assert get_type('Type') is m.typeobj.typeobj

    def test_parent_from_constructor(self):
        mp = Module('parent')
        mc = Module('child', parent=mp)
        assert mc.parent is mp

    def test_parent_from_setter(self):
        mp = Module('parent')
        mc = Module('child')
        mc.set_parent(mp)
        assert mc.parent is mp

    def test_index_values_from_public_table(self):
        m = Module('test')
        m.private_table.add_symbol('a', ValueHolder(5))
        m.public_table.add_symbol('a', ValueHolder(6))
        assert [6, 5] == [m['a'], m.private_table['a']]

@pytest.mark.usefixtures('set_up_env')
class TestClassDefinition:
    def dmy(self): pass
    
    def test_type(self):
        c = ClassDefinition(None, 'test')
        assert get_type('Class') is c.typeobj
        
    def test_type_type(self):
        c = ClassDefinition(None, 'test')
        assert get_type('Type') is c.typeobj.typeobj

@pytest.mark.usefixtures('set_up_env')
class TestClosure:
    def dmy(self): pass
    
    def test_type(self):
        c = Closure(peek_stack_frame(), 'test', self.dmy)
        assert get_type('Closure') is c.typeobj
        
    def test_type_type(self):
        c = Closure(peek_stack_frame(), 'test', self.dmy)
        assert get_type('Type') is c.typeobj.typeobj

@pytest.mark.usefixtures('set_up_env')
class TestFunction:
    def dmy(self): pass
    
    def test_type(self):
        f = Function('test', self.dmy)
        assert get_type('Function') is f.typeobj
        
    def test_type_type(self):
        f = Function('test', self.dmy)
        assert get_type('Type') is f.typeobj.typeobj

@pytest.mark.usefixtures('set_up_env')
class TestMethod:
    def dmy1(self): pass
    def dmy2(self): pass

    owner = [make_object(), make_object()]
    name = ['m1', 'm2']
    content = [dmy1, dmy2]
    param_names = [[], ['a', 'b']]
    
    def test_type(self):
        m = Method(make_object(), 'test', self.dmy1)
        assert get_type('Method') is m.typeobj
        
    def test_type_type(self):
        m = Method(make_object(), 'test', self.dmy1)
        assert get_type('Type') is m.typeobj.typeobj
    
    @pytest.mark.parametrize('owner1', owner)
    @pytest.mark.parametrize('owner2', owner)
    @pytest.mark.parametrize('name1', name)
    @pytest.mark.parametrize('name2', name)
    @pytest.mark.parametrize('content1', content)
    @pytest.mark.parametrize('content2', content)
    @pytest.mark.parametrize('param_names1', param_names)
    @pytest.mark.parametrize('param_names2', param_names)
    def test_eq(self, owner1, owner2, name1, name2, content1, content2, param_names1, param_names2):
        data1 = [owner1, name1, content1, param_names1]
        data2 = [owner2, name2, content2, param_names2]
        assert (Method(owner1, name1, content1, *param_names1) == Method(owner2, name2, content2, *param_names2)) == (data1 == data2)