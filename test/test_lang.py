import pytest
from cacti.lang import SymbolTable 


class TestSymbolTable:
    def test_from_dict_must_be_dict(self):
        with pytest.raises(TypeError):
            SymbolTable(123)
    
    def test_parent_table_must_be_symbol_table(self):
        with pytest.raises(TypeError):
            SymbolTable(parent_table=123)
            
    def test_symbol_must_be_str(self):
        with pytest.raises(TypeError):
            table = SymbolTable()
            table[123] = 123
    
    def test_raises_key_error_for_missing_key(self):
        with pytest.raises(KeyError):
            table = SymbolTable()
            table['x']
        
    def test_value_present_for_key_after_added(self):
        table = SymbolTable()
        table['x'] = 4
        assert 4 == table['x']
        
#     def test_has_values_from_init_map(self):
#         table = SymbolTable({'x': 4, 'y': 'ABC', 'AA123': (1, True, 'G')})
#         expected = [('x', 4), ('y', 'ABC'), ('AA123', (1, True, 'G'))]
#         assert sorted(expected) == sorted(table.items())
        
#     def test_has_values_from_parent_table(self):
#         parent = SymbolTable({'x': 4, 'y': 'ABC', 'AA123': (1, True, 'G')})
#         child = SymbolTable(parent_table=parent)
#         expected = [('x', 4), ('y', 'ABC'), ('AA123', (1, True, 'G'))]
#         assert sorted(expected) == sorted(child.items())
        
