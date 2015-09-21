import pytest

from cacti.exceptions import *
from cacti.runtime import *
from cacti.lang import *
from cacti.builtin import *
from cacti.ast import *

@pytest.mark.usefixtures('set_up_env')
class TestModuleDeclaration:
    def test_process_exports_copies_exports(self):
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
        a_cw = ('a', ConstantWrapperValueHolder(holder_a))
        b_cw = ('b', ConstantWrapperValueHolder(holder_b))
        c_cw = ('c', ConstantWrapperValueHolder(holder_c))
        d_cw = ('d', ConstantWrapperValueHolder(holder_d))
        cws = [a_cw, b_cw, c_cw, d_cw]
        module_cws = list(module.public_table.symbol_holder_iter())
        actual = list(map(lambda e: e in module_cws, cws))
        assert [True, True, True, False] == actual

    def test_exports_are_constant(self):
        stack_frame = StackFrame(make_object(), 'test.module')
        stack_frame.data_store['exports'] = {'a'}
        table = stack_frame.symbol_stack.peek()
        holder_a = ValueHolder(1)
        module = Module('test.module')
        module.private_table.add_symbol('a', holder_a)
        module_dec = ModuleDeclaration('test.module')
        module_dec.process_exports(module, stack_frame)
        with pytest.raises(ConstantValueError):
            module.public_table['a'] = 5

    def test_exports_reflect_change_to_original(self):
        stack_frame = StackFrame(make_object(), 'test.module')
        stack_frame.data_store['exports'] = {'a'}
        table = stack_frame.symbol_stack.peek()
        holder_a = ValueHolder(1)
        module = Module('test.module')
        module.private_table.add_symbol('a', holder_a)
        module_dec = ModuleDeclaration('test.module')
        module_dec.process_exports(module, stack_frame)
        value_before = module.public_table['a']
        module.private_table['a'] = 5
        value_after = module.public_table['a']
        assert [value_before, value_after] == [1, 5]

    def test_process_statement_results_copies_stack_frame_symbols(self):
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
class TestImportStatement:
    def test_imports_all(self):
        holder_a = ValueHolder(1)
        holder_b = ValueHolder(2)
        holder_c = ValueHolder(3)
        holder_d = ValueHolder(4)
        m = Module('test')
        m.public_table.add_symbol('a', holder_a)
        m.public_table.add_symbol('b', holder_b)
        m.public_table.add_symbol('c', holder_c)
        m.public_table.add_symbol('d', holder_d)
        add_module(m)
        impt = ImportStatement('test')
        impt()
        a_cw = ('a', holder_a)
        b_cw = ('b', holder_b)
        c_cw = ('c', holder_c)
        d_cw = ('d', holder_d)
        cws = [a_cw, b_cw, c_cw, d_cw]
        table = peek_stack_frame().symbol_stack.peek()
        table_cws = list(table.symbol_holder_iter())
        actual = list(map(lambda e: e in table_cws, cws))
        assert [True, True, True, True] == actual

    def test_imports_only(self):
        holder_a = ValueHolder(1)
        holder_b = ValueHolder(2)
        holder_c = ValueHolder(3)
        holder_d = ValueHolder(4)
        m = Module('test')
        m.public_table.add_symbol('a', holder_a)
        m.public_table.add_symbol('b', holder_b)
        m.public_table.add_symbol('c', holder_c)
        m.public_table.add_symbol('d', holder_d)
        add_module(m)
        impt = ImportStatement('test', only=['a', 'c'])
        impt()
        a_cw = ('a', holder_a)
        b_cw = ('b', holder_b)
        c_cw = ('c', holder_c)
        d_cw = ('d', holder_d)
        cws = [a_cw, b_cw, c_cw, d_cw]
        table = peek_stack_frame().symbol_stack.peek()
        table_cws = list(table.symbol_holder_iter())
        actual = list(map(lambda e: e in table_cws, cws))
        assert [True, False, True, False] == actual

    def test_imports_alias(self):
        m = Module('test')
        add_module(m)
        impt = ImportStatement('test', alias='abc')
        impt()
        symbol_value = peek_stack_frame().symbol_stack.peek()['abc']
        assert isinstance(symbol_value, ModuleAlias)

    def test_alias_is_constant(self):
        m = Module('test')
        add_module(m)
        impt = ImportStatement('test', alias='abc')
        impt()
        with pytest.raises(ConstantValueError):
            peek_stack_frame().symbol_stack.peek()['abc'] = 123

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
        
        
                