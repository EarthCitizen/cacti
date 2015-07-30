import re
import collections
import copy
import logging
from cacti.exceptions import *
from cacti.debug import get_logger

__all__ = [
    # Functions
    'isvalidhook', 'isvalidsymbol', 'peek_stack_frame', 'pop_stack_frame', 'push_stack_frame',
    
    # Classes
    'StackFrame', 'Callable', 'ConstantValueHolder', 'PropertyGetValueHolder', 'PropertyGetSetValueHolder',
    'SymbolTable', 'SymbolTableChain', 'SymbolTableStack', 'ValueHolder',
]

class _Call:
    def __call__(self, *params):
        return self.call(*params)
    
class Callable(_Call):
    
    def __init__(self, content, *params):
        self.logger = get_logger(self)
        self.__params = params
        self.__content = content
        
    def __check_arity(self, *param_values):
        if len(self.__params) != len(param_values):
            stack_frame = peek_stack_frame()
            kwargs = {
                'caller': str(stack_frame.owner),
                'name': stack_frame.name,
                'exp': len(self.__params),
                'got': len(param_values)
                }
            raise ArityError("{caller}.{name}: Expected {exp} parameter(s) but received {got}".format(**kwargs))
        
    def __make_params_table(self, *param_values):
        param_table = SymbolTable()
        param_iter = iter(param_values)
        for v in self.__params:
            param_table.add_symbol(v, ConstantValueHolder(next(param_iter)))
        return param_table
    
    def call(self, *param_values):
        self.logger.debug("Parameters: {}".format(str(param_values)))
        from cacti.builtin import get_builtin
        self.__check_arity(*param_values)
        param_table = self.__make_params_table(*param_values)
        stack_frame = peek_stack_frame()
        symbol_stack = stack_frame.symbol_stack
        symbol_stack.push(param_table)
        return_value = self.__content()
        symbol_stack.pop()
        if return_value is None:
            return_value = get_builtin('nothing')
        self.logger.debug("Returning: {}".format(str(return_value)))
        return return_value
        
# class ClosureBinding(_Call):
#     def __init__(self, stack_frame, kallable):
#         self.__call_env = copy.copy(stack_frame)
#         self.__callable = kallable
#        
#     def call(self, *params):
#         push_stack_frame(self.__call_env)
#         return_value = self.__callable.call(*params)
#         pop_stack_frame()
#         return return_value

# class FunctionBinding(_Call):
#     def __init__(self, owner, name, kallable):
#         self.__owner = owner
#         self.__name = name
#         self.__callable = kallable
#        
#     def call(self, *params):
#         push_stack_frame(StackFrame(self.__owner, self.__name))
#         return_value = self.__callable.call(*params)
#         pop_stack_frame()
#         return return_value
        
# class MethodBinding(_Call):
#     def __init__(self, owner, method_def):
#         self.logger = get_logger(self)
#         self.__owner = owner
#         self.__method_def = method_def
#        
#     def call(self, *params):
#         self.logger.debug('Start method call')
#         stack_frame = StackFrame(self.__owner, self.__method_def.name)
#         push_stack_frame(stack_frame)
#         self.logger.debug('Pushed new call env')
#         super_self = stack_frame.symbol_stack.peek()
#        
#         selfobj = self.__owner.selfobj
#         superobj = self.__owner.superobj
#        
#         self.logger.debug('Owner: {}'.format(str(self.__owner)))
#        
#         self.logger.debug('Adding self: ' + str(selfobj))
#         super_self.add_symbol('self', ConstantValueHolder(selfobj))
#        
#         self.logger.debug('Adding super: ' + str(superobj))
#         super_self.add_symbol('super', ConstantValueHolder(superobj))
#        
#         return_value = self.__method_def.callable.call(*params)
#         self.logger.debug('Returning: ' + str(return_value))
#        
#         pop_stack_frame()
#         return return_value

STACK = collections.deque()

__debug_stack = False

def __stack_info(prefix, stack_frame):
    owner = stack_frame.owner
    global lvl_str
    global lvl
    #selfobj = stack_frame.symbol_stack['self'] if 'self' in stack_frame.symbol_stack else ''
    #superobj = stack_frame.symbol_stack['super'] if 'super' in stack_frame.symbol_stack else ''
    print((lvl_str * lvl) + "{} {} {} {} {} SELF: {} SUPER: {}".format(
        prefix,
        str(id(owner)),
        str(owner),
        str(owner.typeobj),
        stack_frame.name,
        None, #str(selfobj),
        None #str(superobj)
        ))
    
lvl_str = '\t'
lvl = 0

def push_stack_frame(stack_frame):
    global lvl_str
    global lvl
    if __debug_stack:
        __stack_info("::->PUSH({}): ".format(lvl), stack_frame)
    lvl += 1
    STACK.appendleft(stack_frame)
    
def peek_stack_frame(pos=0):
    if len(STACK) < (pos + 1):
        return None
    stack_frame = STACK[pos]
    if __debug_stack:
        __stack_info("::-PEEK({}): ".format(lvl-1), stack_frame)
    return stack_frame
    
def pop_stack_frame():
    popped = STACK.popleft()
    global lvl_str
    global lvl
    lvl -= 1
    if __debug_stack:
        __stack_info("::<-POPPED({}): ".format(lvl), popped)
    return popped

class StackFrame:
    def __init__(self, owner, name, selfobj=None):
        from cacti.builtin import get_builtin_table
        from cacti.lang import ObjectDefinition
        assert isinstance(owner, ObjectDefinition)
        self.__owner = owner
        self.__name = name
        self.__selfobj = selfobj
        self.__symbol_stack = SymbolTableStack()
        self.__symbol_stack.push(get_builtin_table())
        self.__symbol_stack.push(SymbolTable())
    
    @property
    def owner(self):
        return self.__owner
        
    @property
    def symbol_stack(self):
        return self.__symbol_stack
        
    @property
    def name(self):
        return self.__name
        
    @property
    def selfobj(self):
        return self.__selfobj
    
    def __copy__(self):
        inst_copy = self.__class__(self.__owner, self.__name, self.__selfobj)
        inst_copy.__symbol_stack = copy.copy(self.__symbol_stack)
        return inst_copy
        
    def __repr__(self):
        return str(self)
        
    def __str__(self):
        kwargs = {
            'class_name': self.__class__.__name__,
            'owner_class_name': self.__owner.__class__.__name__,
            'id': id(self.__owner),
            'name': self.__name,
            'stack': str(self.__symbol_stack)
            }
        return "{class_name} {owner_class_name}({id})<{name}>({stack})".format(**kwargs)

class ValueHolder:
    def __init__(self, value):
        self.logger = get_logger(self)
        
        self.__value = value
        
    def get_value(self):
        return_value = self.__value
        self.logger.debug('Get: ' + str(return_value))
        return return_value
    
    def set_value(self, value):
        self.logger.debug('Set: ' + str(value))
        self.__value = value
        
    def __copy__(self):
        return self.__class__(self.__value)
        
    def __repr__(self):
        return str(self)
        
    def __str__(self):
        return self.__class__.__name__ + "(" + str(self.value) + ")"
    
    value = property(get_value, set_value)
    


class ConstantValueHolder(ValueHolder):
    def __init__(self, value):
        super().__init__(value)
        
        self.logger = get_logger(self)
        self.logger.debug("Create with value: {}".format(value))
    
    def set_value(self, value):
        self.logger.debug("Tried to set constant with value: {}".format(value))
        raise ConstantValueError()
    
    value = property(ValueHolder.get_value, set_value)

class PropertyGetSetValueHolder(ValueHolder):
    def __init__(self, getter, setter):
        self.logger = get_logger(self)
        self.logger.debug('Create')
        
        self.__get = getter
        self.__set = setter
    
    def get_value(self):
        return_value = self.__get()
        self.logger.debug('Get: ' + str(return_value))
        return return_value
    
    def set_value(self, value):
        self.logger.debug('Set: ' + str(value))
        self.__set(value)
        
    def __copy__(self):
        return self
    
    value = property(get_value, set_value)

class PropertyGetValueHolder(ConstantValueHolder):
    def __init__(self, getter):
        super().__init__(getter)
        self.logger = get_logger(self)
        self.logger.debug('Create')
        self.__get = getter
    
    def get_value(self):
        return_value = self.__get()
        self.logger.debug('Returning: ' + str(return_value))
        return return_value
    
    def __copy__(self):
        return self
    
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
        self.logger = get_logger(self)
        
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
        
    def __copy__(self):
        parent_copy = copy.copy(self.__parent_table)
        return SymbolTable(
                    from_dict={symbol: copy.copy(content) for symbol, content in self.__table.items()},
                    parent_table=parent_copy,
                    symbol_validator=self.__symbol_validator)
        
    def __contains__(self, key):
        if key in self.__table.keys():
            return True
        if self.__parent_table:
            return key in self.__parent_table
        
        return False
        
    def __getitem__(self, key):
        self.logger.debug("Searching for symbol '{}'".format(key))
        if key in self.__table.keys():
            return_value = self.__table[key].value
            self.logger.debug("For symbol '{}' found: '{}'".format(key, str(return_value)))
            return return_value
        if self.__parent_table:
            self.logger.debug("Searching in parent for symbol '{}'".format(key))
            return_value = self.__parent_table[key]
            self.logger.debug("For symbol '{}' in parent found: '{}'".format(key, str(return_value)))
            return return_value
        
        raise SymbolUnknownError(key)
        
    def __setitem__(self, key, value):
        if key in self.__table.keys():
            self.__table[key].value = value
            self.logger.debug("Set symbol '{}' to: '{}'".format(key, str(value)))
        elif self.__parent_table:
            self.__parent_table[key] = value
            self.logger.debug("Set symbol '{}' in parent to: '{}'".format(key, str(value)))
        else:
            raise SymbolUnknownError(key)
        
    def __repr__(self):
        return str(self)
        
    def __str__(self):
        return self.__class__.__name__ + "(" + str(self.__table) + ", parent_table="+ str(self.__parent_table) + ")"
        
    def to_string(self):
        return str(self)


class SymbolTableChain:
    def __init__(self, *context_chain):
        self.logger = get_logger(self)
        
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
        self.logger.debug("Searching chain for symbol '{}'".format(symbol_name))
        for table in self.__chain:
            if symbol_name in table:
                return_value = table[symbol_name]
                self.logger.debug("For symbol '{}' found: '{}'".format(symbol_name, str(return_value)))
                return return_value
                 
        raise SymbolUnknownError(symbol_name)
    
    def __setitem__(self, symbol_name, symbol_value):
        for table in self.__chain:
            if symbol_name in table:
                table[symbol_name] = symbol_value
                self.logger.debug("Set symbol '{}' in chain to: '{}'".format(symbol_name, str(symbol_value)))
                return
                 
        raise SymbolUnknownError(symbol_name)
    
    def __repr__(self):
        return str(self)
    
    def __str__(self):
        return self.__class__.__name__ + "(" + str(self.__chain) + ")"
        
    def to_string(self):
        return str(self)
            

class SymbolTableStack:
    def __init__(self, *symbol_tables):
        self.logger = get_logger(self)
        self.__stack = collections.deque()
        
        for s in symbol_tables:
            self.push(s)
        
    def push(self, table):
        self.__stack.appendleft(table)
        
    def peek(self):
        return self.__stack[0]
        
    def pop(self):
        return self.__stack.popleft()
    
    def __copy__(self):
        inst_copy =  self.__class__()
        stack_copy = collections.deque()
        for s in self.__stack:
            stack_copy.append(copy.copy(s))
        inst_copy.__stack = stack_copy
        return inst_copy
        
    def __contains__(self, symbol_name):
        for table in self.__stack:
            if symbol_name in table:
                return True
            
        return False
        
    def __getitem__(self, symbol_name):
        self.logger.debug("Searching stack for symbol '{}'".format(symbol_name))
        for table in self.__stack:
            if symbol_name in table:
                return_value = table[symbol_name]
                self.logger.debug("For symbol '{}' in stack found: '{}'".format(symbol_name, str(return_value)))
                return return_value
                 
        raise SymbolUnknownError(symbol_name)
    
    def __setitem__(self, symbol_name, symbol_value):
        for table in self.__stack:
            if symbol_name in table:
                self.logger.debug("Set symbol '{}' in stack to: '{}'".format(symbol_name, str(symbol_value)))
                table[symbol_name] = symbol_value
                return
                 
        raise SymbolUnknownError(symbol_name)
    
    def __repr__(self):
        return str(self)
    
    def __str__(self):
        return self.__class__.__name__ + "(" + str(self.__stack) + ")"
        
    def to_string(self):
        return str(self)
