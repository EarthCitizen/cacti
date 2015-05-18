import re
import collections
from cacti.exceptions import *

__all__ = [
           # Functions
           'isvalidhook', 'isvalidsymbol', 'peek_call_env', 'pop_call_env', 'push_call_env',
           
           # Classes
           'CallEnv', 'Callable', 'ConstantValueHolder', 'PropertyGetValueHolder', 'PropertyGetSetValueHolder', 'SymbolTable', 'SymbolTableChain', 'SymbolTableStack', 'ValueHolder',
           
           'ClosureBinding', 'FunctionBinding', 'MethodBinding'
           ]

class Callable:
    def __init__(self, content, *params):
        self.__params = params
        self.__content = content
        
    def __check_arity(self, *param_values):
        if len(self.__params) != len(param_values):
            call_env = peek_call_env()
            kwargs = {
                'caller': str(call_env.owner),
                'method_name': call_env.name,
                'exp': len(self.__params),
                'got': len(param_values)
                }
            raise ArityError("{caller}.{method_name}: Expected {exp} parameter(s) but received {got}".format(**kwargs))
        
    def __make_params_table(self, *param_values):
        param_table = SymbolTable()
        param_iter = iter(param_values)
        for v in self.__params:
            param_table.add_symbol(v, ConstantValueHolder(next(param_iter)))
        return param_table
    
    def call(self, *param_values):
        self.__check_arity(*param_values)
        param_table = self.__make_params_table(*param_values)
        call_env = peek_call_env()
        symbol_stack = call_env.symbol_stack
        symbol_stack.push(param_table)
        return_value = self.__content()
        symbol_stack.pop()
        return return_value
        
class ClosureBinding:
    def __init__(self, call_env, kallable):
        self.__call_env = call_env
        self.__callable = kallable
        
    def call(self, *params):
        push_call_env(self.__call_env)
        return_value = self.__callable.call(*params)
        pop_call_env()
        return return_value   

class FunctionBinding:
    def __init__(self, owner, name, kallable):
        self.__owner = owner
        self.__name = name
        self.__callable = kallable
        
    def call(self, *params):
        push_call_env(CallEnv(self.__owner, self.__name))
        return_value = self.__callable.call(*params)
        pop_call_env()
        return return_value
        
class MethodBinding:
    def __init__(self, owner, method_def):
        self.__owner = owner
        self.__method_def = method_def
        
    def call(self, *params):
        push_call_env(CallEnv(self.__owner, self.__method_def.name))
        super_self = SymbolTable()
        super_self.add_symbol('self', ConstantValueHolder(self.__owner.selfobj))
        super_self.add_symbol('super', ConstantValueHolder(self.__owner.superobj))
        peek_call_env().symbol_stack.push(super_self)
        return_value = self.__method_def.callable.call(*params)
        pop_call_env()
        return return_value

CALL_ENV_STACK = collections.deque()

def push_call_env(call_env):
    CALL_ENV_STACK.appendleft(call_env)
    
def peek_call_env(pos=0):
    return CALL_ENV_STACK[pos]
    
def pop_call_env():
    popped = CALL_ENV_STACK.popleft()
    return popped

class CallEnv:
    def __init__(self, owner, name):
        self.__owner = owner
        self.__name = name
        self.__symbol_stack = SymbolTableStack()
    
    @property
    def owner(self):
        return self.__owner
        
    @property
    def symbol_stack(self):
        return self.__symbol_stack
        
    @property
    def name(self):
        return self.__name
        
    def __repr__(self):
        return str(self)
        
    def __str__(self):
        #return self.__class__.__name__ + "<" + self.__name + ">" + "(" + str(self.__symbol_stack) + ")"
        return "{} {}({})<{}>({})".format(
            self.__class__.__name__,
            self.__owner.__class__.__name__,
            id(self.__owner),
            self.__name,
            str(self.__symbol_stack))

class ValueHolder:
    def __init__(self, value):
        self.__value = value
        
    def get_value(self):
        return self.__value
    
    def set_value(self, value):
        self.__value = value
        
    def __repr__(self):
        return str(self)
        
    def __str__(self):
        return self.__class__.__name__ + "(" + str(self.value) + ")"
    
    value = property(get_value, set_value)


class ConstantValueHolder(ValueHolder):
    def set_value(self, value):
        raise ConstantValueError()
    
    value = property(ValueHolder.get_value, set_value)
    
class PropertyGetSetValueHolder(ValueHolder):
    def __init__(self, getter, setter):
        self.__get = getter
        self.__set = setter
    
    def get_value(self):
        return self.__get.call()
    
    def set_value(self, value):
        self.__set.call(value)
    
    value = property(get_value, set_value)

class PropertyGetValueHolder(ConstantValueHolder):
    def __init__(self, getter):
        self.__get = getter
    
    def get_value(self):
        return self.__get.call()
    
    value = property(get_value,ConstantValueHolder.set_value)

__VALID_SYMBOL_PATTERN__ = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')

__HOOKS__ = [
        r'\(\)', r'\[\]', r'\.',
        r'\*', r'\/', r'\+', r'\-',
        r'\*\=', r'\/\=', r'\+\=', r'\-\=',
    ]

__VALID_HOOK_PATTERN__ =  re.compile(r'^' + r'|'.join(__HOOKS__) + r'$')

def isvalidsymbol(symbol):
    return True if isinstance(symbol, str) and __VALID_SYMBOL_PATTERN__.match(symbol) else False

def isvalidhook(symbol):
    return True if isinstance(symbol, str) and __VALID_HOOK_PATTERN__.match(symbol) else False

class SymbolTable:
    def __init__(self, from_dict={}, parent_table=None, symbol_validator=isvalidsymbol):
        if not isinstance(from_dict, dict):
            raise TypeError("from_map must be a 'dict'")
        
        self.__symbol_validator = symbol_validator
        
        self.__table = {}
        
        for symbol,  content in from_dict.items():
            self.add_symbol(symbol, content)
        
        if parent_table and (not isinstance(parent_table, SymbolTable)):
            raise TypeError("parent_table must be a 'SymbolTable'")
        
        self.__parent_table = parent_table
        
    def add_symbol(self, symbol, content):
        self.__check_symbol(symbol)
        self.__check_content(content)
        self.__table[symbol] = content
        
    def __check_symbol(self, symbol):
        if not self.__symbol_validator(symbol):
            raise SymbolError("Invalid symbol '{}'".format(symbol))
        
    def __check_content(self, symbol_content):
        if not isinstance(symbol_content, ValueHolder):
            raise SymbolContentError("Symbol content must be a 'ValueHolder'")
        
    def __contains__(self, key):
        if key in self.__table.keys():
            return True
        if self.__parent_table:
            return key in self.__parent_table
        
        return False
        
    def __getitem__(self, key):
        if key in self.__table.keys():
            return self.__table[key].value
        if self.__parent_table:
            return self.__parent_table[key]
        
        raise SymbolUnknownError(key)
        
    def __setitem__(self, key, value):
        if key in self.__table.keys():
            self.__table[key].value = value
        elif self.__parent_table:
            self.__parent_table[key] = value
        else:
            raise SymbolUnknownError(key)
        
    def __repr__(self):
        return str(self)
        
    def __str__(self):
        return self.__class__.__name__ + "(" + str(self.__table) + ", parent_table="+ str(self.__parent_table) + ")"


class SymbolTableChain:
    def __init__(self, *context_chain):
        for t in context_chain:
            if not isinstance(t, SymbolTable) and not isinstance(t, SymbolTableChain):
                raise TypeError("All elements in the chain must be a 'SymbolTable'")
        
        self.__chain = context_chain
        
    @property
    def chain(self):
        return self.__chain
    
    def __contains__(self, symbol_name):
        for table in self.__chain:
            if symbol_name in table:
                return True
            
        return False
    
    def __getitem__(self, symbol_name):
        for table in self.__chain:
            if symbol_name in table:
                return table[symbol_name]
                 
        raise SymbolUnknownError(symbol_name)
    
    def __setitem__(self, symbol_name, symbol_value):
        for table in self.__chain:
            if symbol_name in table:
                table[symbol_name] = symbol_value
                return
                 
        raise SymbolUnknownError(symbol_name)
    
    def __repr__(self):
        return str(self)
    
    def __str__(self):
        return self.__class__.__name__ + "(" + str(self.__chain) + ")"
            

class SymbolTableStack:
    def __init__(self):
        self.__stack = collections.deque()
        
    def push(self, table):
        self.__stack.appendleft(table)
        
    def peek(self):
        return self.__stack[0]
        
    def pop(self):
        return self.__stack.popleft()
        
    def __contains__(self, symbol_name):
        for table in self.__stack:
            if symbol_name in table:
                return True
            
        return False
        
    def __getitem__(self, symbol_name):
        for table in self.__stack:
            if symbol_name in table:
                return table[symbol_name]
                 
        raise SymbolUnknownError(symbol_name)
    
    def __setitem__(self, symbol_name, symbol_value):
        for table in self.__stack:
            if symbol_name in table:
                table[symbol_name] = symbol_value
                return
                 
        raise SymbolUnknownError(symbol_name)
    
    def __repr__(self):
        return str(self)
    
    def __str__(self):
        return self.__class__.__name__ + "(" + str(self.__stack) + ")"
