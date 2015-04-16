__all__ = [
           # Functions
           'isvalidsymbol',
           
           # Exceptions
           'ConstantValueError', 'SymbolError',
           
           # Classes
           'ConstantValueHolder', 'SymbolTable', 'ValueHolder', 'VariableValueHolder'
           ]

import re

class ValueHolder:
    def __init__(self, value):
        self.__value = value
        
    def get_value(self):
        return self.__value
    
    value = property(get_value)

class ConstantValueError(Exception): pass

class ConstantValueHolder(ValueHolder):
    def set_value(self, value):
        raise ConstantValueError()
    
    value = property(ValueHolder.get_value, set_value)

class VariableValueHolder(ValueHolder):
    def set_value(self, value):
        self.__value = value
    
    value = property(ValueHolder.get_value, set_value)

class SymbolError(Exception): pass

__VALID_SYMBOL_PATTERN__ = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')

def isvalidsymbol(symbol):
    return True if isinstance(symbol, str) and __VALID_SYMBOL_PATTERN__.match(symbol) else False

class SymbolContext:
    def __init__(self, *context_chain):
        self.__chain = context_chain
        
    @property
    def chain(self):
        return list(self.__chain)
    
    def __getitem__(self, symbol_name):
        symbol_found = None
        for table in self.__chain:
            try:
                symbol_found = table[symbol_name]
            except KeyError:
                raise SymbolError("Unknown symbol '{}'".format(symbol_name))
            
        return symbol_found.get_value()

class SymbolTable:
    def __init__(self, from_dict={}, parent_table=None):
        if not isinstance(from_dict, dict):
            raise TypeError("from_map must be a 'dict'")
        
        for symbol in from_dict.keys():
            self.__check_symbol__(symbol)
        
        if parent_table and (not isinstance(parent_table, SymbolTable)):
            raise TypeError("parent_table must be a 'SymbolTable'")
        
        self.__table = dict(from_dict)
        self.__parent_table = parent_table
        
    def __check_symbol__(self, symbol):
        if not isvalidsymbol(symbol):
            raise SymbolError("Invalid symbol '{}'".format(symbol))
        
    def __getitem__(self, key):
        if key in self.__table.keys():
            return self.__table[key]
        if self.__parent_table:
            return self.__parent_table[key]
        else:
            raise KeyError("Key '{}' not found".format(key))
    
    def __setitem__(self, symbol, value):
        self.__check_symbol__(symbol)
        self.__table[symbol] = value
    
