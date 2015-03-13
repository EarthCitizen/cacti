from collections import defaultdict


class SymbolTable:
    def __init__(self, from_dict={}, parent_table=None):
        if not isinstance(from_dict, dict):
            raise TypeError("from_map must be a 'dict'")
        
        if parent_table and (not isinstance(parent_table, SymbolTable)):
            raise TypeError("parent_table must be a 'SymbolTable'")
        
        self.__table = dict(from_dict)
        self.__parent_table = parent_table
        
    def __getitem__(self, key):
        if key in self.__table.keys():
            return self.__table[key]
        if self.__parent_table:
            return self.__parent_table[key]
        else:
            raise KeyError("Key '{}' not found".format(key))
    
    def __setitem__(self, key, value):
        if not isinstance(key, str):
            raise TypeError("Key must be a 'str'")
        self.__table[key] = value
    
