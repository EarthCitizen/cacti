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
            return x.hook_table['*'](y)
        function_callable = Callable(function_content, 'x', 'y')
        function = Function('foo', function_callable)
        main_object = get_builtin('Object').hook_table['()'].call()
        main_env = CallEnv(main_object, 'main')
        main_stack = main_env.symbol_stack
        main_table = SymbolTable()
        main_table.add_symbol(function.name, ConstantValueHolder(function))
        main_stack.push(main_table)
        push_call_env(main_env)
        expr = OperationExpression(ReferenceExpression('foo'), '()', ValueExpression(make_integer(10)), ValueExpression(make_integer(2)))
        assert 20 == expr().primitive
        
class TestPropertyExpression:
    def test_resolves_multiple_properties(self):
        prop_list = ['id', 'type', 'name']
        obj = make_string('test')
        prop_expr = PropertyExpression(ValueExpression(obj), *prop_list)
        assert prop_expr().primitive == 'Integer'
        
@pytest.mark.usefixtures('set_up_env')
class TestReferenceExpression:
    def test_returns_dereferenced_value(self):
        table = SymbolTable()
        table.add_symbol('X', ConstantValueHolder(123))
        call_env = peek_call_env()
        call_env.symbol_stack.push(table)
        expr = ReferenceExpression('X')
        assert 123 == expr()

class TestValueExpression:
    def test_returns_value(self):
        obj = make_object()
        expr = ValueExpression(obj)
        assert obj is expr()

@pytest.mark.usefixtures('set_up_env')
class TestAssignmentStatement:
    def test_assigns_value(self):
        table = peek_call_env().symbol_stack.peek()
        table.add_symbol('x', ValueHolder(make_integer(5)))
        stmt = AssignmentStatement('x', ValueExpression(make_integer(10)))
        stmt()
        x = peek_call_env().symbol_stack['x']
        assert x.primitive == 10

@pytest.mark.usefixtures('set_up_env')
class TestValDeclarationStatement:
    def test_creates_symbol_with_value(self):
        val_stmt = ValDeclarationStatement('x', ValueExpression(make_integer(5)))
        val_stmt()
        call_env = peek_call_env()
        assert call_env.symbol_stack['x'].primitive == 5
    
    def test_creates_constant_value(self):
        val_stmt = ValDeclarationStatement('x', ValueExpression(make_integer(5)))
        val_stmt()
        with pytest.raises(ConstantValueError):
            call_env = peek_call_env()
            call_env.symbol_stack['x'] = make_integer(99)

@pytest.mark.usefixtures('set_up_env')
class TestVarDeclarationStatement:
    def test_creates_symbol_with_value(self):
        var_stmt = VarDeclarationStatement('x', ValueExpression(make_integer(5)))
        var_stmt()
        call_env = peek_call_env()
        assert call_env.symbol_stack['x'].primitive == 5
        
    def test_creates_changeable_value(self):
        var_stmt = VarDeclarationStatement('x', ValueExpression(make_integer(5)))
        var_stmt()
        call_env = peek_call_env()
        call_env.symbol_stack['x'] = make_integer(99)
        assert call_env.symbol_stack['x'].primitive == 99
        
class ShowCalledExpression:
        def __init__(self):
            self.called = False
        
        def __call__(self):
            self.called = True

class TestBlock:
    def test_evals_all_expressions(self):
        exprs = [ShowCalledExpression(), ShowCalledExpression(), ShowCalledExpression()]
        block = Block(*exprs)
        block()
        evals = list(filter(lambda e: e.called, exprs))
        assert len(exprs) == len(evals)
        
        
                