import pytest
from cacti.exceptions import *
from cacti.runtime import *
from cacti.builtin import *
from cacti.lang import *

@pytest.mark.usefixtures('set_up_env')
class TestCallable:
    def test_adds_params_to_env(self):
        def content():
            return peek_stack_frame().symbol_stack['a']
            
        c = Callable(content, 'a')
        i = make_integer(5)
        assert c(i) == i
        
    def test_raises_arity_error_for_wrong_param_count(self):
        def content(): pass
        c = Callable(content, 'a', 'b')
        i = make_integer(5)
        with pytest.raises(ArityError):
            c(i)

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
        owner = make_object()
        
        def get_value():
            return make_integer(456)
        
        #get_value_callable = Callable(get_value)
        
        get_method_def = MethodDefinition('get_value', get_value)
        
        _property = PropertyGetSetValueHolder(get_method_def.make_method(owner), None)
        
        assert make_integer(456).primitive == _property.get_value().primitive
     
    def test_setter_executed(self):
        owner = make_object()
        owner.add_var('x', make_integer(999))
         
        def get_value():
            table = peek_stack_frame().symbol_stack
            #TODO: For property of operator
            #return table['self'].hook_table['.']('x')
            return table['self']['x']
         
        get_method_def = MethodDefinition('some_prop', get_value)
         
        def set_value():
            table = peek_stack_frame().symbol_stack
            table['self']['x'] = table['value']
         
        set_method_def = MethodDefinition('some_prop', set_value, 'value')
         
        _property = PropertyGetSetValueHolder(get_method_def.make_method(owner), set_method_def.make_method(owner))
        _property.set_value(make_integer(100))
         
        assert make_integer(100).primitive == _property.get_value().primitive

@pytest.mark.usefixtures('set_up_env')
class TestPropertyGetValueHolder:
    def test_getter_executed(self):
        def get_value():
            return make_integer(456)
        
        get_method_def = MethodDefinition('get_value', get_value)
        
        owner = make_object()
         
        _property = PropertyGetValueHolder(get_method_def.make_method(owner))
        
        assert make_integer(456).primitive == _property.get_value().primitive
      
    def test_setter_throws_constant_error(self):
        def get_value():
            return make_integer(456)
        
        get_method_def = MethodDefinition('get_value', get_value)
        
        owner = make_object()
        
        _property = PropertyGetValueHolder(get_method_def.make_method(owner))
         
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

class TestIsValidModule:
    valid_symbols = ['x', 'X', '_', 'X_.G.B.C', 'AAAAAAA', 'a_a_a.bb.__c123', '_123', '_123._456.A', '_____6', 'dddd____']
    
    invalid_symbols = ['1', '1_', ' ', ' x', ' x ', '123abc', '3', 'A.b.c.', '.', '.a.b', 3]
    
    @pytest.mark.parametrize('symbol', valid_symbols)
    def test_valid_symbols(self, symbol):
        assert True == isvalidmodule(symbol)
    
    @pytest.mark.parametrize('symbol', invalid_symbols)
    def test_invalid_symbold(self, symbol):
        assert False == isvalidmodule(symbol)
    

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
        
    def test_symbol_holder_iter_single_layer(self):
        holder_x = ValueHolder(4)
        holder_y = ValueHolder(5)
        holder_z = ValueHolder(6)
        table = SymbolTable({'x': holder_x, 'y': holder_y, 'z': holder_z})
        assert {'x': holder_x, 'y': holder_y, 'z': holder_z} == dict(table.symbol_holder_iter())
    
    def test_symbol_holder_iter_nested_tables(self):
        holder_x = ValueHolder(4)
        grandparent = SymbolTable({'x': holder_x})
        holder_y = ValueHolder(5)
        parent = SymbolTable({'y': holder_y}, parent_table=grandparent)
        holder_z = ValueHolder(6)
        child = SymbolTable({'z': holder_z}, parent_table=parent)
        assert {'x': holder_x, 'y': holder_y, 'z': holder_z} == dict(child.symbol_holder_iter())
    
    def test_symbol_holder_iter_child_shadows_parents(self):
        holder_x = ValueHolder(4)
        grandparent_a = ValueHolder(4.5)
        grandparent = SymbolTable({'x': holder_x, 'a': grandparent_a})
        holder_y = ValueHolder(5)
        parent_a = ValueHolder(5.5)
        parent = SymbolTable({'y': holder_y, 'a': parent_a}, parent_table=grandparent)
        holder_z = ValueHolder(6)
        child_a = ValueHolder(6.5)
        child = SymbolTable({'z': holder_z, 'a': child_a}, parent_table=parent)
        expected = {'x': holder_x, 'y': holder_y, 'z': holder_z, 'a': child_a}
        assert expected == dict(child.symbol_holder_iter())
        
    def test_symbol_holder_iter_parent_shadows_grandparent(self):
        holder_x = ValueHolder(4)
        grandparent_a = ValueHolder(4.5)
        grandparent = SymbolTable({'x': holder_x, 'a': grandparent_a})
        holder_y = ValueHolder(5)
        parent_a = ValueHolder(5.5)
        parent = SymbolTable({'y': holder_y, 'a': parent_a}, parent_table=grandparent)
        holder_z = ValueHolder(6)
        child = SymbolTable({'z': holder_z}, parent_table=parent)
        expected = {'x': holder_x, 'y': holder_y, 'z': holder_z, 'a': parent_a}
        assert expected == dict(child.symbol_holder_iter())
    
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