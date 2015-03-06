
class SymbolTable(dict):
    def __init__(self, from_map={}, parent_table=None):
        super().__init__(from_map)
        self.__parent_table = parent_table
        
    def __missing__(self, key):
        value = None
        if self.__parent_table:
            value = self.__parent_table[key]
        return value

