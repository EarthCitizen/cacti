import pytest

from cacti.exceptions import *
from cacti.runtime import *
from cacti.lang import *
from cacti.builtin import *
from cacti.ast import *

@pytest.mark.usefixtures('set_up_env')
class TestModuleDeclaration:
    def test_process_exports_copies_exports_to_public_table(self):
        stack_frame = StackFrame(make_object(), 'test.module')
        stack_frame.data_store['exports'] = {'a', 'b', 'c'}
        table = stack_frame.symbol_stack.peek()
        holder_a = ValueHolder(1)
        holder_b = ValueHolder(2)
        holder_c = ValueHolder(3)
        holder_d = ValueHolder(4)
        module = Module('test.module')
        module.private_table.add_symbol('a', holder_a)
        module.private_table.add_symbol('b', holder_b)
        module.private_table.add_symbol('c', holder_c)
        module.private_table.add_symbol('d', holder_d)
        module_dec = ModuleDeclaration('test.module')
        module_dec.process_exports(module, stack_frame)
        unexpected = {('d', holder_d)}
        expected = {('a', holder_a), ('b', holder_b), ('c', holder_c)}
        actual = set(module.public_table.symbol_holder_iter())
        assert expected.issubset(actual) and not(unexpected.issubset(actual))

    def test_process_statement_results_copies_stack_frame_symbols_to_private_table(self):
        stack_frame = StackFrame(make_object(), 'test.module')
        table = stack_frame.symbol_stack.peek()
        holder_a = ValueHolder(1)
        holder_b = ValueHolder(2)
        holder_c = ValueHolder(3)
        holder_d = ValueHolder(4)
        module = Module('test.module')
        table.add_symbol('a', holder_a)
        table.add_symbol('b', holder_b)
        table.add_symbol('c', holder_c)
        table.add_symbol('d', holder_d)
        module_dec = ModuleDeclaration('test.module')
        module_dec.process_statement_results(module, stack_frame)
        expected = {('a', holder_a), ('b', holder_b), ('c', holder_c), ('d', holder_d)}
        actual = set(module.private_table.symbol_holder_iter())
        assert expected.issubset(actual)

@pytest.mark.usefixtures('set_up_env')
class TestOperationExpression:
    def test_returns_expected_value(self):
        def function_content():
            stack_frame = peek_stack_frame()
            symbol_stack = stack_frame.symbol_stack
            x = symbol_stack['x']
            y = symbol_stack['y']
            return x.hook_table['*'](y)
        function = Function('foo', function_content, 'x', 'y')
        table = peek_stack_frame().symbol_stack.peek()
        table.add_symbol(function.name, ConstantValueHolder(function))
        expr = OperationExpression(ReferenceExpression('foo'), '()',
                    ValueExpression(make_integer(10)),
                    ValueExpression(make_integer(2)))
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
        stack_frame = peek_stack_frame()
        stack_frame.symbol_stack.push(table)
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
        table = peek_stack_frame().symbol_stack.peek()
        table.add_symbol('x', ValueHolder(make_integer(5)))
        stmt = AssignmentStatement('x', ValueExpression(make_integer(10)))
        stmt()
        x = peek_stack_frame().symbol_stack['x']
        assert x.primitive == 10

@pytest.mark.usefixtures('set_up_env')
class TestExportStatement:
    def test_single_symbol(self):
        expt = ExportStatement('x')
        frame = peek_stack_frame()
        expt()
        assert frame.data_store['exports'] == {'x'}

    def test_multiple_symbols(self):
        expt = ExportStatement('x', 'y', 'z')
        frame = peek_stack_frame()
        expt()
        assert frame.data_store['exports'] == {'x', 'y', 'z'}

@pytest.mark.usefixtures('set_up_env')
class TestValDeclarationStatement:
    def test_creates_symbol_with_value(self):
        val_stmt = ValDeclarationStatement('x', ValueExpression(make_integer(5)))
        val_stmt()
        stack_frame = peek_stack_frame()
        assert stack_frame.symbol_stack['x'].primitive == 5
    
    def test_creates_constant_value(self):
        val_stmt = ValDeclarationStatement('x', ValueExpression(make_integer(5)))
        val_stmt()
        with pytest.raises(ConstantValueError):
            stack_frame = peek_stack_frame()
            stack_frame.symbol_stack['x'] = make_integer(99)

@pytest.mark.usefixtures('set_up_env')
class TestVarDeclarationStatement:
    def test_creates_symbol_with_value(self):
        var_stmt = VarDeclarationStatement('x', ValueExpression(make_integer(5)))
        var_stmt()
        stack_frame = peek_stack_frame()
        assert stack_frame.symbol_stack['x'].primitive == 5
        
    def test_creates_changeable_value(self):
        var_stmt = VarDeclarationStatement('x', ValueExpression(make_integer(5)))
        var_stmt()
        stack_frame = peek_stack_frame()
        stack_frame.symbol_stack['x'] = make_integer(99)
        assert stack_frame.symbol_stack['x'].primitive == 99
        
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
        
        
                