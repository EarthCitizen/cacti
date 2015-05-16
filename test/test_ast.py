import pytest

from cacti.exceptions import *
from cacti.runtime import *
from cacti.lang import *
from cacti.builtin import *
from cacti.ast import *

class TestOperationExpression:
    def test_returns_expected_value(self):
        def function_content():
            call_env = peek_call_env()
            symbol_stack = call_env.symbol_stack
            x = symbol_stack['x']
            y = symbol_stack['y']
            return x * y
        function_callable = Callable(function_content, 'x', 'y')
        function = Function('foo', function_callable)
        main_object = get_builtin('Object').hook_table['()'].call()
        main_env = CallEnv(main_object, 'main')
        main_stack = main_env.symbol_stack
        main_table = SymbolTable()
        main_table.add_symbol(function.name, ConstantValueHolder(function))
        main_stack.push(main_table)
        push_call_env(main_env)
        expr = OperationExpression(ReferenceExpression('foo'), '()', ValueExpression(10), ValueExpression(2))
        assert 20 == expr()

class TestReferenceExpression:
    def test_returns_dereferenced_value(self):
        table = SymbolTable()
        table.add_symbol('X', ConstantValueHolder(123))
        call_env = CallEnv(object(), 'test')
        call_env.symbol_stack.push(table)
        push_call_env(call_env)
        expr = ReferenceExpression('X')
        assert 123 == expr()

class TestValueExpression:
    def test_returns_value(self):
        obj = object()
        expr = ValueExpression(obj)
        assert obj is expr()

class TestValDeclarationStatement:
    @pytest.fixture()
    def set_up_env(self):
        call_env = CallEnv(make_object(), 'main')
        call_env.symbol_stack.push(SymbolTable())
        push_call_env(call_env)
    
    @pytest.mark.usefixtures('set_up_env')
    def test_creates_symbol_with_value(self):
        val_stmt = ValDeclarationStatement('x', ValueExpression(make_integer(5)))
        val_stmt()
        call_env = peek_call_env()
        assert call_env.symbol_stack['x'].primitive == make_integer(5).primitive
    
    @pytest.mark.usefixtures('set_up_env')
    def test_creates_constant(self):
        val_stmt = ValDeclarationStatement('x', ValueExpression(make_integer(5)))
        val_stmt()
        with pytest.raises(ConstantValueError):
            call_env = peek_call_env()
            call_env.symbol_stack['x'] = make_integer(99)