from cacti.runtime import *

__all__ = [
           # Classes
           'Callable', 'ClojureBinding', 'FunctionBinding', 'MethodBinding',
           
           'ClassDefinition', 'MethodDefinition', 'ObjectDefinition', 'PropertyDefinition', 'TypeDefinition'
           ]
           

#print('EXECUTING BUILTIN')

BUILTIN_SYMBOLS = SymbolTable()

def register_type_definition(type_def, name):
    BUILTIN_SYMBOLS[name] = ConstantValueHolder(type_def)

def get_type_definition(name):
    return BUILTIN_SYMBOLS[name].get_value()

class UnsupportedMethodError(Exception): pass

class UnknownPropertyError(Exception): pass

class ArityError(Exception): pass

def get_object():
    return ObjectDefinition(get_type_definition('ObjectDefinition'), None)


# All ObjectDefinition Instances Have This
class ObjectDefinition:
    def __init__(self, superobj, *, typeobj=None, name=''):
        self.__typeobj = typeobj
        self.__name = name
        self.__selfobj = self
        self.__superobj = superobj
        self.__field_table = SymbolTable()
        
        parent_hook_table = superobj.hook_table if superobj else None
        self.__hook_table = SymbolTable(parent_table=parent_hook_table, symbol_validator=isvalidhook)
        
        parent_property_table = superobj.property_table if superobj else None
        self.__property_table = SymbolTable(parent_table=parent_property_table)
        
        self.__public_table = self.__property_table
        self.__private_table = SymbolTableChain(self.__property_table, self.__field_table)
        
    def set_typeobj(self, typeobj):
        self.__typeobj = typeobj
        
    def set_selfobj(self, selfobj):
        self.__selfobj = selfobj
    
    @property
    def public_table(self):
        return self.__public_table
        
    @property
    def private_table(self):
        return self.__private_table
        
    @property
    def hook_table(self):
        return self.__hook_table
        
    @property
    def property_table(self):
        return self.__property_table
        
    @property
    def selfobj(self):
        return self.__selfobj
    
    @property
    def superobj(self):
        return self.__superobj
        
    @property
    def typeobj(self):
        return self.__typeobj
        
    @property
    def name(self):
        return self.__name
        
    def add_hook(self, hook_name, hook_callable):
        binding = MethodBinding(self, hook_name, hook_callable)
        self.__hook_table.add_symbol(hook_name, ConstantValueHolder(binding))
    
    def add_val(self, val_name, val_value):
        self.__field_table.add_symbol(val_name, ConstantValueHolder(val_value))
    
    def add_var(self, var_name, var_value):
        self.__field_table.add_symbol(var_name, ValueHolder(var_value))
        
    def add_method(self, method_name, method_callable):
        bound_callable = MethodBinding(self, method_name, method_callable)
        method = ObjectDefinition(METHOD_TYPEDEF, OBJECT)
        method.add_hook('()', bound_callable)
        const_value = ConstantValueHolder(method)
        self.__property_table.add_symbol(method_name, const_value)
        
    def add_property(self, property_name, get_callable, set_callable):
        value_holder = None
        private_table = self.__private_table
        
        if get_callable is None and set_callable is None:
            value_holder = ValueHolder()
        elif get_callable is not None and set_callable is not None:
            value_holder = PropertyGetValueHolder(
                MethodBinding(self, property_name, get_callable))
        elif get_callable is not None and set_callable is None:
            value_holder = PropertyGetSetValueHolder(
                MethodBinding(self, property_name, get_callable),
                MethodBinding(self, property_name, set_callable))
        else:
            raise Exception('TBD')
        
        self.__property_table.add_symbol(property_name, value_holder)
    
    def __str__(self):
        return '{}<{}>'.format(self.typeobj.name, id(self))

class TypeDefinition(ObjectDefinition):
    def __init__(self, superobj, name, *, typeobj=None):
        super().__init__(superobj, typeobj=typeobj, name=name)
    
    def __str__(self):
        return '{}<{}>'.format('Type', self.name)
        
class ClassDefinition(ObjectDefinition):
    def __init__(self, superobj, name, *, typeobj=None, superclass=None):
        super().__init__(superobj, typeobj=typeobj, name=name)
        self.__superclass = superclass
        self.__hook_defs = []
        self.__val_defs = []
        self.__var_defs = []
        self.__method_defs = []
        self.__property_defs = []
        
    def set_superclass(self, superclass):
        self.__superclass = superclass
        
    @property
    def superclass(self):
        return self.__superclass
        
    @property
    def hook_definitions(self):
        return self.__hook_defs
        
    @property
    def val_definitions(self):
        return self.__val_defs
        
    @property
    def var_definitions(self):
        return self.__var_defs
        
    @property
    def method_definitions(self):
        return self.__method_defs
        
    @property
    def property_definitions(self):
        return self.__property_defs
        
    def add_hook_definition(self, hook_def):
        self.__hook_defs += [hook_def]
        
    def add_val_definition(self, val_def):
        self.__val_defs += [val_def]
        
    def add_var_definition(self, var_def):
        self.__var_def += [var_def]
        
    def add_method_definition(self, method_def):
        self.__method_defs += [method_def]
        
    def add_property_definition(self, prop_def):
        self.__property_defs += [prop_def]
        
    def __str__(self):
        return '{}<{}>'.format('Class', self.name)

class MethodDefinition:
    def __init__(self, method_name, method_callable):
        self.__method_name = method_name
        self.__method_callable = method_callable
        
    @property
    def name(self):
        return self.__method_name
        
    @property
    def callable(self):
        return self.__method_callable
        
class PropertyDefinition:
    def __init__(self, property_name, *, getter_callable=None, setter_callable=None):
        self.__property_name = property_name
        self.__getter_callable = getter_callable
        self.__setter_callable = setter_callable
        
    @property
    def name(self):
        return self.__property_name
        
    @property
    def getter_callable(self):
        return self.__getter_callable
        
    @property
    def setter_callable(self):
        return self.__setter_callable
        
class ValDefinition:
    def __init__(self, val_name, val_init_expr):
        self.__val_name = val_name
        self.__val_init_expr = val_init_expr
        
    @property
    def name(self):
        return self.__val_name
        
    @property
    def init_expr(self):
        return self.__val_init_expr
    
class Callable:
    def __init__(self, content, *params):
        self.__params = params
        self.__content = content
        
    def __check_arity(self, *param_values):
        if len(self.__params) != len(param_values):
            raise ArityError('Parameter count does not match')
        
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
        
class ClojureBinding:
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
    def __init__(self, owner, name, kallable):
        self.__owner = owner
        self.__name = name
        self.__callable = kallable
        
    def call(self, *params):
        push_call_env(CallEnv(self.__owner, self.__name))
        super_self = SymbolTable()
        super_self.add_symbol('self', ConstantValueHolder(self.__owner.selfobj))
        super_self.add_symbol('super', ConstantValueHolder(self.__owner.superobj))
        peek_call_env().symbol_stack.push(super_self)
        return_value = self.__callable.call(*params)
        pop_call_env()
        return return_value

# class Callable(ObjectDefinition):
#     def __init__(self, type_def, name, *param_names):
#         super().__init__(type_def, get_object())
#         self.__name = name
#         self.__param_names = param_names
#         
#     def call(self, caller, *params):
#         self.check_arity(caller, *params)
#         
#     def check_arity(self, caller, *called_params):
#         if self.arity != len(called_params):
#             kwargs = {'caller': caller.type.name, 'method_name': self.__name, 'exp': self.arity, 'got': len(called_params)}
#             raise SyntaxError("{caller}.{method_name}: Expected {exp} parameter(s) but received {got}".format(**kwargs))
#     
    
# class PyMethod(Method):
#     def __init__(self, method_name, function, *param_names):
#         type_def = get_type_definition('Method')
#         super().__init__(type_def, method_name, *param_names)
#         self.__function = function
#         
#     def call(self, target, *params):
#         super().call(target, *params)
#         if self.__function:
#             return self.__function(target, *params)
#         
# class TypeMethod(PyMethod):
#     def __init__(self):
#         super().__init__('type', lambda target: target.type)
# 
# class IdMethod(PyMethod):
#     def __init__(self):
#         super().__init__('id', lambda target: target.id)
#         
# class NameMethod(PyMethod):
#     def __init__(self):
#         super().__init__('name', lambda target: target.name)
#         
# class NewMethod(PyMethod):
#     def __init__(self):
#         super().__init__('new', lambda target, *params: target.get_instance(*params))
#         
# class ToStringMethod(PyMethod):
#     def __init__(self):
#         super().__init__('to_string', lambda target: target.to_string())
#         
# class SuperMethod(PyMethod):
#     def __init__(self):
#         super().__init__('super', lambda target: target.super)
# 
# class HasMethodMethod(PyMethod):
#     def __init__(self):
#         function = lambda target, *params: target.has_method(*params)
#         param_names = ('method_name',)
#         super().__init__('has_method', function, param_names)
#         
# class PyBinaryOpMethod(PyMethod):
#     def __init__(self, method_name):
#         lookup = {'+': lambda a, b: a+b, '-': lambda a, b: a-b, '*': lambda a, b: a*b, '/': lambda a, b: a/b}
#         super().__init__(method_name, lookup[method_name], 'a', 'b')
#         
#     def call(self, caller, *params):
#         super().call(self, *params)
#         return self.__op_method(caller.raw_value, params[0].raw_value)
#         
# class PyFunction(Function):
#     def __init__(self, function_name, function, *param_names):
#         type_def = get_type_definition('Function')
#         super().__init__(type_def, function_name, *param_names)
#         self.__function = function
#         
#     def call(self, *params):
#         super().call(self, *params)
#         if self.__function:
#             return self.__function(*params)
#         