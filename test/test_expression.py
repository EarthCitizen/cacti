import pytest

from cacti.runtime import *
from cacti.lang import *
from cacti.builtin import *
from cacti.expression import *

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