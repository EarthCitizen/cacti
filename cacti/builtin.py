import operator
import types
import logging
from cacti.debug import get_logger
from cacti.runtime import *
from cacti.lang import *
from cacti.exceptions import *

__all__ = [
    'get_type', 'get_builtin', 'get_builtin_superobj', 'get_builtin_table',
    'initialize_builtins',
    'make_class', 'make_float', 'make_integer', 'make_main', 'make_object', 'make_string'
]

def make_object():
    logger = get_logger(make_object)
    logger.debug('Start')
    obj = get_builtin('Object').hook_table['()'].call()
    logger.debug('Returning: ' + str(obj))
    return obj

def make_class(name, superclass_name='Object', *, val_defs=None, var_defs=None, method_defs=None):
    logger = get_logger(make_class)
    logger.debug("name={}, superclass_name={}".format(repr(name), repr(superclass_name)))
    superobj = make_object()
    typeobj = get_type('Class')
    call_env = peek_stack_frame()
    if call_env and (superclass_name in call_env.symbol_stack):
        superclass = call_env.symbol_stack[superclass_name]
    else:
        superclass = get_builtin(superclass_name)
    classdef = ClassDefinition(superobj, name, typeobj=typeobj, superclass=superclass)
    
    classdef.add_hook(MethodDefinition('()', _hook_new_callable_content))
    
    logger.debug("Returning: {}".format(repr(classdef)))
    
    return classdef

def make_main():
    typedef_superobj = make_object()
    main_typedef = TypeDefinition(typedef_superobj, 'Main')
    main_typedef.set_typeobj(get_type('Type'))
    main_superobj = make_object()
    main = ObjectDefinition(main_superobj, name='main')
    main.set_typeobj(main_typedef)
    return main

def make_string(value=''):
    assert isinstance(value, str)
    obj = get_builtin('String').hook_table['()'].call()
    obj.primitive = value
    obj.to_native_repr = types.MethodType(lambda self: "make_string({})".format(repr(self.primitive)), obj)
    return obj

def make_float(value=float(0)):
    assert (isinstance(value, float) or isinstance(value, int))
    value = float(value)
    obj = get_builtin('Float').hook_table['()'].call()
    obj.primitive = value
    obj.to_native_repr = types.MethodType(lambda self: "make_float({})".format(repr(self.primitive)), obj)
    return obj

def make_integer(value=0):
    assert isinstance(value, int)
    obj = get_builtin('Integer').hook_table['()'].call()
    obj.primitive = value
    obj.to_native_repr = types.MethodType(lambda self: "make_integer({})".format(repr(self.primitive)), obj)
    return obj

class _StubCallable:
    def __init__(self, content):
        self.__content = content
    
    def call(self, *param_values):
        self.__content()

### HOOK NEW ###
def _hook_new_callable_content():
    class_def = peek_stack_frame().owner
    superclass_def = class_def.superclass
    superobj = superclass_def.hook_table['()'].call() if superclass_def else None
    obj = ObjectDefinition(superobj, typeobj=class_def)
    _init_object_def_from_class_def(obj, class_def)
    return obj

def _make_hook_new_method_def():
    def hook_new_body():
        class_def = peek_stack_frame().owner
        superclass_def = class_def.superclass
        superobj = superclass_def.hook_table['()'].call() if superclass_def else None
        obj = ObjectDefinition(superobj, typeobj=class_def)
        _init_object_def_from_class_def(obj, class_def)
        
        return obj
        
    hook_new_callable = Callable(_hook_new_callable_content)
    
    return MethodDefinition('()', hook_new_callable)


### HOOK PROPERTY OF ###
def _make_hook_property_of_method_def():
    def hook_property_of_body():
        call_owner = peek_stack_frame(1).owner
        curr_env = peek_stack_frame()
        curr_owner = curr_env.owner
        property_name = curr_env.symbol_stack['property_name']
        
        if call_owner is curr_owner:
            return curr_owner.private_table[property_name]
        else:
            return curr_owner.public_table[property_name]
            
    hook_property_of_callable = Callable(hook_property_of_body, 'property_name')
            
    return MethodDefinition('.', hook_property_of_callable)

def _make_method_def_op_not_supported(operation, *param_names):
    def do_raise():
        call_env = peek_stack_frame()
        raise OperationNotSupportedError(call_env.owner.selfobj.typeobj.name, call_env.name)
    method_callable = _StubCallable(do_raise)
    return MethodDefinition(operation, do_raise)
    
BUILTIN_INIT_DATA = {
        'Object': {
                'superclass': None,
                
                'hooks': {
                        _make_hook_new_method_def()
                    },
                
                'hook_defs': {
                        #_make_hook_property_of_method_def(),
                        
                        _make_method_def_op_not_supported('()'),
                        _make_method_def_op_not_supported('[]'),
                        _make_method_def_op_not_supported('*'),
                        _make_method_def_op_not_supported('/'),
                        _make_method_def_op_not_supported('+'),
                        _make_method_def_op_not_supported('-'),
                        
                        _make_method_def_op_not_supported('*='),
                        _make_method_def_op_not_supported('/='),
                        _make_method_def_op_not_supported('+='),
                        _make_method_def_op_not_supported('-=')
                    },
                    
                'method_defs': {
                    },
                    
                'property_defs': {
                        PropertyDefinition('string', getter_method_def=MethodDefinition('get', lambda: make_string(peek_call_env().symbol_stack['self'].to_string()))),
                    }
            }
    }

def _init_class_def_from_data(class_def):
    object_dict = BUILTIN_INIT_DATA[class_def.name]
    hooks = object_dict['hooks']
    hook_defs = object_dict['hook_defs']
    method_defs = object_dict['method_defs']
    property_defs = object_dict['property_defs']
    
    for hook in hooks:
        class_def.add_hook(hook)
    
    for hook_def in hook_defs:
        class_def.add_hook_definition(hook_def)
        
    for method_def in method_defs:
        class_def.add_method_definition(method_def)
    
    for property_def in property_defs:
        class_def.add_property_definition(property_def)

        
def _init_object_def_from_class_def(object_def, class_def):
    
    for hook_def in class_def.hook_definitions:
        object_def.add_hook(hook_def)
        
    for method_def in class_def.method_definitions:
        object_def.add_method(method_def)
        
    for prop_def in class_def.property_definitions:
        object_def.add_property(prop_def)
        
    call_env = StackFrame(object_def, 'self')
    call_env.symbol_stack.push(object_def.field_table)
    push_stack_frame(call_env)
    
    # Initialize constants
    for val_def in class_def.val_definitions:
        object_def.add_val(val_def.name, val_def.init_expr())
        
    # Initialize vars after constants
    for var_def in class_def.var_definitions:
        object_def.add_var(var_def.name, var_def.init_expr())
        
    pop_stack_frame()
        
    object_def.set_typeobj(class_def)

_TYPES = SymbolTable()
_BUILTINS = SymbolTable()
__BUILTIN_SUPEROBJ = None

def add_type(symbol_name, object_instance):
    _TYPES.add_symbol(symbol_name, ConstantValueHolder(object_instance))
    
def get_type(symbol_name):
    if symbol_name not in _TYPES:
        t = _make_type(symbol_name)
        add_type(symbol_name, t)
        return t
    else:
        return _TYPES[symbol_name]

def add_builtin(symbol_name, object_instance):
    _BUILTINS.add_symbol(symbol_name, ConstantValueHolder(object_instance))
    
def get_builtin(symbol_name):
    return _BUILTINS[symbol_name]
    
def get_builtin_superobj():
    return __BUILTIN_SUPEROBJ

def get_builtin_table():
    return _BUILTINS

def _bootstrap_basic_types():
    __BUILTIN_SUPEROBJ = ObjectDefinition(None)
    
    
    __typedef_typedef_superobj = __BUILTIN_SUPEROBJ #__object_classdef.hook_table['()'].call()
    __typedef_typedef = TypeDefinition.__new__(TypeDefinition)
    __typedef_typedef.set_name('Type')
    add_type('Type', __typedef_typedef)
    __typedef_typedef.__init__(__typedef_typedef_superobj, 'Type')
    __typedef_typedef.set_typeobj(__typedef_typedef)
    
    
    # BOOTSTRAP THE CLASS DEFINITION FOR Object
    __object_classdef_superobj = __BUILTIN_SUPEROBJ
    __object_classdef = ClassDefinition(__object_classdef_superobj, 'Object')
    _init_class_def_from_data(__object_classdef)
    _init_object_def_from_class_def(__object_classdef_superobj, __object_classdef)
    
    
    __classdef_typedef_superobj = __BUILTIN_SUPEROBJ #__object_classdef.hook_table['()'].call()
    __classdef_typedef = TypeDefinition(__classdef_typedef_superobj, 'Class')
    __classdef_typedef.set_typeobj(__typedef_typedef)
    
    __object_classdef.set_typeobj(__classdef_typedef)
    
    add_builtin(__object_classdef.name, __object_classdef)
    
    add_type(__classdef_typedef.name, __classdef_typedef)
    
def _make_type(type_name):
    superobj = get_builtin_superobj() #get_builtin('Object').hook_table['()'].call()
    typedef = TypeDefinition.__new__(TypeDefinition)
    typedef.set_name(type_name)
    add_type(typedef.name, typedef)
    typedef.__init__(superobj, type_name)
    typedef.set_typeobj(get_type('Type'))

_PRIMITIVE_OPERATION_FUNCTIONS = {
        '*': operator.mul,
        '/': operator.floordiv,
        '+': operator.add,
        '-': operator.sub
    }

def _make_primitive_op_method_def(operation):
    
    def callable_content():
        call_env = peek_stack_frame()
        selfobj = call_env.symbol_stack['self']
        other = call_env.symbol_stack['other']
        result = _PRIMITIVE_OPERATION_FUNCTIONS[operation](selfobj.primitive, other.primitive)
        new_object = get_builtin(selfobj.typeobj.name).hook_table['()']()
        new_object.primitive = result
        return new_object
    
    return MethodDefinition(operation, callable_content, 'other')
        

_PRIMITIVE_OPERATION_METHOD_DEFS = {
        '*': _make_primitive_op_method_def('*'),
        '/': _make_primitive_op_method_def('/'),
        '+': _make_primitive_op_method_def('+'),
        '-': _make_primitive_op_method_def('-')
    }

def _make_string_class():
    superobj = make_object()
    typeobj = get_type('Class')
    superclass = get_builtin('Object')
    classdef = ClassDefinition(superobj, 'String', typeobj=typeobj, superclass=superclass)
    
    def new_callable_content():
        obj = _hook_new_callable_content()
        obj.primitive = ''
        obj.to_string = types.MethodType(lambda self: self.primitive, obj)
        return obj
        
    classdef.add_hook(MethodDefinition('()', new_callable_content))
    
    classdef.add_hook_definition(_PRIMITIVE_OPERATION_METHOD_DEFS['+'])
    
    string_callable_content = lambda: peek_stack_frame().symbol_stack['self']
    string_prop_def = PropertyDefinition('string', getter_method_def=MethodDefinition('get', string_callable_content))
    classdef.add_property_definition(string_prop_def)
    
    add_builtin(classdef.name, classdef)

def _make_numeric_class(class_name, converter):
    superobj = make_object()
    typeobj = get_type('Class')
    superclass = get_builtin('Object')
    classdef = ClassDefinition(superobj, class_name, typeobj=typeobj, superclass=superclass)
    
    def new_callable_content():
        obj = _hook_new_callable_content()
        obj.primitive = 0
        obj.to_string = types.MethodType(lambda self: str(self.primitive), obj)
        return obj
        
    classdef.add_hook(MethodDefinition('()', Callable(new_callable_content)))
    
    for operation in ['*', '/', '+', '-']:
        classdef.add_hook_definition(_PRIMITIVE_OPERATION_METHOD_DEFS[operation])
        
    string_callable_content = lambda: make_string(str(peek_stack_frame().symbol_stack['self'].primitive))
    string_prop_def = PropertyDefinition('string', getter_method_def=MethodDefinition('get', string_callable_content))
    classdef.add_property_definition(string_prop_def)
    
    add_builtin(classdef.name, classdef)
    
def _make_nothing():
    typedef_superobj = make_object()
    nothing_typedef = TypeDefinition(typedef_superobj, 'Nothing')
    nothing_typedef.set_typeobj(get_type('Type'))
    nothing_superobj = make_object()
    nothing = ObjectDefinition(nothing_superobj, name='nothing')
    nothing.set_typeobj(nothing_typedef)
    add_builtin(nothing.name, nothing)
    
def _make_false():
    typedef_superobj = make_object()
    nothing_typedef = TypeDefinition(typedef_superobj, 'False')
    nothing_typedef.set_typeobj(get_type('Type'))
    nothing_superobj = make_object()
    nothing = ObjectDefinition(nothing_superobj, name='false')
    nothing.set_typeobj(nothing_typedef)
    add_builtin(nothing.name, nothing)
    
def _make_true():
    typedef_superobj = make_object()
    nothing_typedef = TypeDefinition(typedef_superobj, 'True')
    nothing_typedef.set_typeobj(get_type('Type'))
    nothing_superobj = make_object()
    nothing = ObjectDefinition(nothing_superobj, name='true')
    nothing.set_typeobj(nothing_typedef)
    add_builtin(nothing.name, nothing)

def _make_function_print():
    def fn_print():
        value = peek_stack_frame().symbol_stack['value'].public_table['string']
        print(value.primitive)
    
    fn = Function('print', fn_print, 'value')
    add_builtin(fn.name, fn)
    
def _make_function_log_debug():
    import logging
    def fn():
        print("Setting to DEBUG")
        logging.getLogger().setLevel(logging.DEBUG)
    
    fn_callable = Callable(fn)
        
    fn = Function('log_debug', fn_callable)
    add_builtin(fn.name, fn)

def _make_function_log_info():
    import logging
    def fn():
        print("Setting to INFO")
        logging.getLogger().setLevel(logging.INFO)
    
    fn_callable = Callable(fn)
        
    fn = Function('log_info', fn_callable)
    add_builtin(fn.name, fn)

def initialize_builtins():
    _bootstrap_basic_types()
    _make_type('Function')
    _make_type('Closure')
    #_make_type('Method')
    _make_string_class()
    _make_nothing()
    _make_false()
    _make_true()
    _make_function_print()
    _make_function_log_debug()
    _make_function_log_info()
    _make_numeric_class('Integer', int)
    _make_numeric_class('Float', float)
    
