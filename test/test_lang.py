import pytest
from cacti.lang import *


class TestValueHolder:
    def test_accepts_value(self):
        holder = ValueHolder(123)
        assert holder.value == 123
 
class TestConstantValueHolder:
    def test_accepts_value(self):
        holder = ConstantValueHolder(123)
        assert holder.value == 123
        
    def test_value_change_not_allowed(self):
        with pytest.raises(ConstantValueError):
            holder = ConstantValueHolder(123)
            holder.value = 456
            
class TestVariableValueHolder:
    def test_accepts_value(self):
        holder = VariableValueHolder(123)
        assert holder.value == 123
        
    def test_value_change_allowed(self):
        holder = VariableValueHolder(123)
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
            SymbolTable({'1d': 1})
    
    def test_parent_table_must_be_symbol_table(self):
        with pytest.raises(TypeError):
            SymbolTable(parent_table=123)
            
    def test_symbol_must_be_valid(self):
        with pytest.raises(SymbolError):
            table = SymbolTable()
            table['1d'] = 123
    
    def test_raises_key_error_for_missing_key(self):
        with pytest.raises(KeyError):
            table = SymbolTable()
            table['x']
        
    def test_value_present_for_key_after_added(self):
        table = SymbolTable()
        table['x'] = 4
        assert 4 == table['x']
        
    def test_value_fetched_from_parent(self):
        parent = SymbolTable({'x': 4})
        child = SymbolTable(parent_table=parent)
        assert 4 == child['x']
        
    def test_value_fetched_from_grandparent(self):
        grandparent = SymbolTable({'x': 4})
        parent = SymbolTable(parent_table=grandparent)
        child = SymbolTable(parent_table=parent)
        assert 4 == child['x']
        
    def test_has_values_from_init_map(self):
        table = SymbolTable({'x': 4, 'y': 'ABC', 'AA123': (1, True, 'G')})
        expected = {'x': 4, 'y': 'ABC', 'AA123': (1, True, 'G')}
        actual = {}
        actual['x'] = table['x']
        actual['y'] = table['y']
        actual['AA123'] = table['AA123']
        assert sorted(expected) == sorted(actual)
        
        
