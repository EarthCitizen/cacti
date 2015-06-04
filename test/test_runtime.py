import pytest
from cacti.exceptions import *
from cacti.runtime import *
from cacti.builtin import *
from cacti.lang import *

class TestValueHolder:
    def test_accepts_value(self):
        holder = ValueHolder(123)
        assert holder.value == 123
        
    def test_value_change_allowed(self):
        holder = ValueHolder(123)
        holder.value = 456
 
class TestConstantValueHolder:
    def test_accepts_value(self):
        holder = ConstantValueHolder(123)
        assert holder.value == 123
        
    def test_value_change_not_allowed(self):
        with pytest.raises(ConstantValueError):
            holder = ConstantValueHolder(123)
            holder.value = 456

@pytest.mark.usefixtures('set_up_env')            
class TestPropertyGetSetValueHolder:
    def test_getter_executed(self):
        def get_value():
            return make_integer(456)
        
        get_value_callable = Callable(get_value)
        
        method_def = MethodDefinition('get_value', get_value_callable)
        
        get_binding = MethodBinding(make_object(), method_def)
         
        _property = PropertyGetSetValueHolder(get_binding, None)
        
        assert make_integer(456).primitive == _property.get_value().primitive
     
    def test_setter_executed(self):
        owner = make_object()
        owner.add_var('x', make_integer(999))
         
        def get_value():
            table = peek_call_env().symbol_stack
            return table['self'].hook_table['.'].call('x')
         
        get_callable = Callable(get_value)
        get_method_def = MethodDefinition('some_prop', get_callable)
        bound_get = MethodBinding(owner, get_method_def)
         
        def set_value():
            table = peek_call_env().symbol_stack
            table['self']['x'] = table['value']
         
        set_callable = Callable(set_value, 'value')
        set_method_def = MethodDefinition('some_prop', set_callable)
        bound_set = MethodBinding(owner, set_method_def)
         
        _property = PropertyGetSetValueHolder(bound_get, bound_set)
        _property.set_value(make_integer(100))
         
        assert make_integer(100).primitive == _property.get_value().primitive

@pytest.mark.usefixtures('set_up_env')
class TestPropertyGetValueHolder:
    def test_getter_executed(self):
        def get_value():
            return make_integer(456)
        
        get_value_callable = Callable(get_value)
        
        method_def = MethodDefinition('get_value', get_value_callable)
        
        get_binding = MethodBinding(make_object(), method_def)
         
        _property = PropertyGetValueHolder(get_binding)
        
        assert make_integer(456).primitive == _property.get_value().primitive
      
    def test_setter_throws_constant_error(self):
        def get_value():
            return make_integer(456)
        
        get_value_callable = Callable(get_value)
        
        method_def = MethodDefinition('get_value', get_value_callable)
        
        get_binding = MethodBinding(make_object(), method_def)
         
        _property = PropertyGetValueHolder(get_binding)
         
        with pytest.raises(ConstantValueError):
            _property.set_value(make_integer(100))

            
class TestIsValidSymbol:
    
    valid_symbols = ['x', 'X', '_', 'X_', 'AAAAAAAAAAAAA', 'a_a_a', '_123', '_____6', 'dddd____']
    
    invalid_symbols = ['1', '1_', ' ', ' x', ' x ', '123abc', 3]

    @pytest.mark.parametrize('symbol', valid_symbols)
    def test_valid_symbols(self, symbol):
        assert True == isvalidsymbol(symbol)
    
    @pytest.mark.parametrize('symbol', invalid_symbols)
    def test_invalid_symbold(self, symbol):
        assert False == isvalidsymbol(symbol)


class TestSymbolTable:
    def test_from_dict_must_be_dict(self):
        with pytest.raises(TypeError):
            SymbolTable(123)
            
    def test_from_dict_must_contain_valid_symbols(self):
        with pytest.raises(SymbolError):
            SymbolTable({'1d': ValueHolder(5)})
            
    def test_from_dict_must_contain_valid_symbol_contents(self):
        with pytest.raises(SymbolContentError):
            SymbolTable({'d': 1})
    
    def test_parent_table_must_be_symbol_table(self):
        with pytest.raises(TypeError):
            SymbolTable(parent_table=123)
            
    def test_symbol_must_be_valid(self):
        with pytest.raises(SymbolError):
            table = SymbolTable()
            table['1d'] = 123
    
    def test_raises_symbol_error_for_missing_key(self):
        with pytest.raises(SymbolError):
            table = SymbolTable()
            table['x']
        
    def test_set_value(self):
        table = SymbolTable({'x': ValueHolder(4)})
        table['x'] = 4
        assert 4 == table['x']
        
    def test_set_value_in_parent(self):
        grand_parent_table = SymbolTable({'z': ValueHolder(4)})
        parent_table = SymbolTable({'y': ValueHolder(3)}, parent_table=grand_parent_table)
        table = SymbolTable({'x': ValueHolder(2)}, parent_table=parent_table)
        table['z'] = 6
        assert 6 == table['z']
        
    def test_value_fetched_from_parent(self):
        parent = SymbolTable({'x': ValueHolder(4)})
        child = SymbolTable(parent_table=parent)
        assert 4 == child['x']
        
    def test_value_fetched_from_grandparent(self):
        grandparent = SymbolTable({'x': ValueHolder(4)})
        parent = SymbolTable(parent_table=grandparent)
        child = SymbolTable(parent_table=parent)
        assert 4 == child['x']
        
    def test_has_values_from_init_map(self):
        table = SymbolTable({'x': ValueHolder(4), 'y': ValueHolder('ABC'), 'AA123': ValueHolder((1, True, 'G'))})
        expected = {'x': 4, 'y': 'ABC', 'AA123': (1, True, 'G')}
        actual = {}
        actual['x'] = table['x']
        actual['y'] = table['y']
        actual['AA123'] = table['AA123']
        assert sorted(expected) == sorted(actual)
        
    def test_contains_symbol(self):
        table = SymbolTable({'x': ValueHolder(4)})
        assert 'x' in table
    
    def test_not_contains_symbol(self):
        table = SymbolTable()
        assert 'x' not in table
        
    def test_contains_symbol_in_parent_table(self):
        parent_table = SymbolTable({'y': ValueHolder(9)})
        table = SymbolTable({'x': ValueHolder(4)}, parent_table=parent_table)
        assert 'y' in table
    
class TestSymbolTableChain:
    def test_chain_elements_must_be_symbol_tables(self):
        with pytest.raises(TypeError):
            SymbolTableChain(1)
            
    def test_accepts_symbol_table(self):
        st = SymbolTable()
        SymbolTableChain(st)
        
    def test_accepts_symbol_table_chain(self):
        stc = SymbolTableChain()
        SymbolTableChain(stc)
    
    def test_gets_value_from_chain(self):
        t1 = SymbolTable({'x': ValueHolder(4)})
        t2 = SymbolTable({'y': ValueHolder(3)})
        t3 = SymbolTable({'z': ValueHolder(2)})     
        chain = SymbolTableChain(t3, t2, t1)
        assert 4 == chain['x']
        
    def test_gets_value_from_front_of_chain(self):
        t1 = SymbolTable({'x': ValueHolder(4)})
        t2 = SymbolTable({'y': ValueHolder(3)})
        t3 = SymbolTable({'x': ValueHolder(2)})     
        chain = SymbolTableChain(t3, t2, t1)
        assert 2 == chain['x']

    def test_sets_value_in_chain(self):
        t1 = SymbolTable({'x': ValueHolder(4)})
        t2 = SymbolTable({'y': ValueHolder(3)})
        t3 = SymbolTable({'z': ValueHolder(2)})     
        chain = SymbolTableChain(t3, t2, t1)
        chain['x'] = 16
        assert 16 == chain['x']
        
    def test_contains_true(self):
        t1 = SymbolTable({'x': ValueHolder(4)})
        t2 = SymbolTable({'y': ValueHolder(3)})
        t3 = SymbolTable({'z': ValueHolder(2)})
        chain = SymbolTableChain(t3, t2, t1)
        assert True == ('x' in chain)
    
    def test_contains_false(self):
        t1 = SymbolTable({'x': ValueHolder(4)})
        t2 = SymbolTable({'y': ValueHolder(3)})
        t3 = SymbolTable({'z': ValueHolder(2)})
        chain = SymbolTableChain(t3, t2, t1)
        assert False == ('c' in chain)

class TestSymbolTableStack:
    
    def test_adds_tables_from_ctor(self):
        t1 = SymbolTable({'x': ValueHolder(4)})
        t2 = SymbolTable({'y': ValueHolder(3)})
        t3 = SymbolTable({'z': ValueHolder(2)})
        stack = SymbolTableStack(t1, t2, t3)
        assert [4, 3, 2] == [stack['x'], stack['y'], stack['z']]
        
    def test_shadows_values(self):
        t1 = SymbolTable({'x': ValueHolder(4)})
        t2 = SymbolTable({'y': ValueHolder(3)})
        t3 = SymbolTable({'z': ValueHolder(2)})
        t4 = SymbolTable({'x': ValueHolder(-1)})
        stack = SymbolTableStack(t1, t2, t3, t4)
        assert [-1, 3, 2] == [stack['x'], stack['y'], stack['z']]
    
    def test_gets_value_from_stack(self):
        t1 = SymbolTable({'x': ValueHolder(4)})
        t2 = SymbolTable({'y': ValueHolder(3)})
        t3 = SymbolTable({'z': ValueHolder(2)})
        stack = SymbolTableStack()
        stack.push(t1)
        stack.push(t2)
        stack.push(t3)
        assert 4 == stack['x']
        
    def test_gets_value_from_front_of_stack(self):
        t1 = SymbolTable({'x': ValueHolder(4)})
        t2 = SymbolTable({'y': ValueHolder(3)})
        t3 = SymbolTable({'x': ValueHolder(2)})
        stack = SymbolTableStack()
        stack.push(t1)
        stack.push(t2)
        stack.push(t3)
        assert 2 == stack['x']

    def test_sets_value_in_stack(self):
        t1 = SymbolTable({'x': ValueHolder(4)})
        t2 = SymbolTable({'y': ValueHolder(3)})
        t3 = SymbolTable({'z': ValueHolder(2)})
        stack = SymbolTableStack()
        stack.push(t1)
        stack.push(t2)
        stack.push(t3)
        stack['x'] = 16
        assert 16 == stack['x']
        
    def test_contains_true(self):
        t1 = SymbolTable({'x': ValueHolder(4)})
        t2 = SymbolTable({'y': ValueHolder(3)})
        t3 = SymbolTable({'z': ValueHolder(2)})
        stack = SymbolTableStack()
        stack.push(t1)
        stack.push(t2)
        stack.push(t3)
        assert True == ('x' in stack)
    
    def test_contains_false(self):
        t1 = SymbolTable({'x': ValueHolder(4)})
        t2 = SymbolTable({'y': ValueHolder(3)})
        t3 = SymbolTable({'z': ValueHolder(2)})
        stack = SymbolTableStack()
        stack.push(t1)
        stack.push(t2)
        stack.push(t3)
        assert False == ('c' in stack)