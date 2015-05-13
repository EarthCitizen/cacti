import pytest

from cacti.runtime import *
from cacti.expression import *

class TestOperationExpression:
    def test_returns_called_value(self):
        pass

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