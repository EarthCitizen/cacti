from cacti.lang import SymbolTable 


class TestSymbolTable:
    def test_none_for_missing_key(self):
        table = SymbolTable()
        assert table['x'] == None
        
    def test_key_not_present_after_missin_key(self):
        table = SymbolTable()
        table['x']
        assert 'x' not in table.keys()

    def test_value_present_for_key_after_added(self):
        table = SymbolTable()
        table['x'] = 4
        assert 4 == table['x']
        
    def test_has_values_from_init_map(self):
        table = SymbolTable({'x': 4, 'y': 'ABC', 'AA123': (1, True, 'G')})
        expected = [('x', 4), ('y', 'ABC'), ('AA123', (1, True, 'G'))]
        assert sorted(expected) == sorted(table.items())
        
    def test_has_values_from_parent_table(self):
        parent = SymbolTable({'x': 4, 'y': 'ABC', 'AA123': (1, True, 'G')})
        child = SymbolTable(parent_table=parent)
        expected = [('x', 4), ('y', 'ABC'), ('AA123', (1, True, 'G'))]
        assert sorted(expected) == sorted(child.items())
        
