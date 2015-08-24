import pytest

from cacti.ast import *
from cacti.builtin import *
from cacti.lang import *
from cacti.runtime import peek_stack_frame, ConstantValueHolder


@pytest.mark.usefixtures('set_up_env')
class TestObject:
    def test_type_correct(self):
        obj = make_object()
        assert obj.typeobj is get_builtin('Object')

    def test_isa_throws_error_if_not_class_param(self):
        from cacti.exceptions import InvalidTypeError
        with pytest.raises(InvalidTypeError):
            i = make_integer()
            s = make_string('test')
            s.hook_table['isa'](i)
        
    def test_isa_self(self):
        obj = make_object()
        obj_class = get_builtin('Object')
        
        assert obj.hook_table['isa'](obj_class) is get_builtin('true')
        
    def test_isa_super(self):
        curr_frame = peek_stack_frame()
        symbol_table = curr_frame.symbol_stack.peek()
        
        foo_class = make_class('Foo')
        symbol_table.add_symbol(foo_class.name, ConstantValueHolder(foo_class))
        
        subfoo_class = make_class('SubFoo', 'Foo')
        subfoo_obj = subfoo_class.hook_table['()']()
        
        assert subfoo_obj.hook_table['isa'](foo_class) is get_builtin('true')
    
    def test_isa_super_super(self):
        curr_frame = peek_stack_frame()
        symbol_table = curr_frame.symbol_stack.peek()
        
        foo_class = make_class('Foo')
        symbol_table.add_symbol(foo_class.name, ConstantValueHolder(foo_class))
        
        subfoo_class = make_class('SubFoo', 'Foo')
        symbol_table.add_symbol(subfoo_class.name, ConstantValueHolder(subfoo_class))
        
        bottomfoo_class = make_class('BottomFoo', 'SubFoo')
        bottomfoo_obj = bottomfoo_class.hook_table['()']()
        
        assert bottomfoo_obj.hook_table['isa'](foo_class) is get_builtin('true')
        
    def test_isa_middle(self):
        curr_frame = peek_stack_frame()
        symbol_table = curr_frame.symbol_stack.peek()
        
        foo_class = make_class('Foo')
        symbol_table.add_symbol(foo_class.name, ConstantValueHolder(foo_class))
        
        subfoo_class = make_class('SubFoo', 'Foo')
        symbol_table.add_symbol(subfoo_class.name, ConstantValueHolder(subfoo_class))
        
        bottomfoo_class = make_class('BottomFoo', 'SubFoo')
        bottomfoo_obj = bottomfoo_class.hook_table['()']()
        
        assert bottomfoo_obj.hook_table['isa'](subfoo_class) is get_builtin('true')
        
    def test_isa_bottom(self):
        curr_frame = peek_stack_frame()
        symbol_table = curr_frame.symbol_stack.peek()
        
        foo_class = make_class('Foo')
        symbol_table.add_symbol(foo_class.name, ConstantValueHolder(foo_class))
        
        subfoo_class = make_class('SubFoo', 'Foo')
        symbol_table.add_symbol(subfoo_class.name, ConstantValueHolder(subfoo_class))
        
        bottomfoo_class = make_class('BottomFoo', 'SubFoo')
        bottomfoo_obj = bottomfoo_class.hook_table['()']()
        
        assert bottomfoo_obj.hook_table['isa'](bottomfoo_class) is get_builtin('true')

@pytest.mark.usefixtures('set_up_env')
class TestPrint:
    def test_sends_output_to_stdout(self, capsys):
        fn = OperationExpression(ReferenceExpression('print'), '()', ValueExpression(make_string("Hello World!")))
        fn()
        out, err = capsys.readouterr()
        assert "Hello World!\n" == out
    
    def test_calls_string_operation(self, capsys):
        class CustomStringOperation(ObjectDefinition):
            def to_string(self):
                return "This is the custom string"
        fn = OperationExpression(ReferenceExpression('print'), '()', ValueExpression(CustomStringOperation(None)))
        fn()
        out, err = capsys.readouterr()
        assert "This is the custom string\n" == out

class TestType:
    def test_type_correct(self):
        _type = get_type('Type')
        type_type = _type.typeobj
        assert id(_type) == id(type_type)
        
class TestClass:        
    def test_type_correct(self):
        class_type = get_type('Class').typeobj
        type_type = get_type('Type')
        assert id(class_type) == id(type_type)
        