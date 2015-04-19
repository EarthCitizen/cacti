import pytest
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
