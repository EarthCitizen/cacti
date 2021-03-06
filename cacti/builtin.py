import operator
import types
import logging
from cacti.debug import get_logger
from cacti.runtime import *
from cacti.lang import *
from cacti.exceptions import *

__all__ = [
    'get_type', 'get_builtin', 'get_builtin_table', 'get_method_superobj',
    'initialize_builtins',
    'make_class', 'make_float', 'make_integer', 'make_main', 'make_object', 'make_string'
]

_POST_BOOTSTRAP_OBJECT_INIT = []
_METHOD_SUPEROBJ = None

def make_object():
    logger = get_logger(make_object)
    logger.debug('Start')
    if 'Object' in _BUILTINS:
        obj = get_builtin('Object').hook_table['()'].call()
    else:
        obj = make_post_bootstrap_object()
    logger.debug('Returning: ' + str(obj))
    return obj
    
def make_post_bootstrap_object():
    logger = get_logger(make_object)
    logger.debug('Start')
    obj = ObjectDefinition(None)
    global _POST_BOOTSTRAP_OBJECT_INIT
    _POST_BOOTSTRAP_OBJECT_INIT += [obj]
    logger.debug('Returning: ' + str(obj))
    return obj
    
def get_method_superobj():
    global _METHOD_SUPEROBJ
    if not _METHOD_SUPEROBJ:
        _METHOD_SUPEROBJ = make_post_bootstrap_object()
    return _METHOD_SUPEROBJ

def make_class(name, superclass_name='Object', *, val_defs=None, var_defs=None, method_defs=None):
    logger = get_logger(make_class)
    logger.debug("name={}, superclass_name={}".format(repr(name), repr(superclass_name)))
    stack_frame = peek_stack_frame()
    if stack_frame and (superclass_name in stack_frame.symbol_stack):
        superclass = stack_frame.symbol_stack[superclass_name]
    else:
        superclass = get_builtin(superclass_name)
    classdef = ClassDefinition(None, name, superclass=superclass)
    
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
        
    #hook_new_callable = Callable(_hook_new_callable_content)
    
    return MethodDefinition('()', hook_new_body)

### HOOK ISA ###
def _make_hook_isa_method_def():
    def hook_isa_body():
        curr_frame = peek_stack_frame()
        kind = curr_frame.symbol_stack['kind']

        if not isinstance(kind, TypeDefinition):
            msg = "'{}' is not an instance of Type. 'isa' requires a type for the right parameter.".format(kind.to_string())
            raise InvalidTypeError(msg)

        obj = curr_frame.owner.selfobj
        
        while True:
            if obj.typeobj is kind:
                return get_builtin('true')
            elif obj.superobj:
                obj = obj.superobj
            else:
                return get_builtin('false')

    return MethodDefinition('isa', hook_isa_body, 'kind')
        

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
        stack_frame = peek_stack_frame()
        raise OperationNotSupportedError(stack_frame.owner.selfobj.typeobj.name, stack_frame.name)
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
                        _make_hook_isa_method_def(),
                        
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
        
    stack_frame = StackFrame(object_def, 'self')
    stack_frame.symbol_stack.push(object_def.field_table)
    push_stack_frame(stack_frame)
    
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
    
def get_builtin_table():
    return _BUILTINS

def _bootstrap_basic_types():
    # Make the root of all types
    
    type_type = TypeDefinition(None, 'Type')
    type_type.set_typeobj(type_type)
    add_type(type_type.name, type_type)
    
    method_type = TypeDefinition(None, 'Method', typeobj=type_type)
    add_type(method_type.name, method_type)
    
    # Make Class used to instantiate Object
    __classdef_typedef = TypeDefinition(None, 'Class', typeobj=type_type)
    add_type(__classdef_typedef.name, __classdef_typedef)
    
    # BOOTSTRAP THE CLASS DEFINITION FOR Object
    __object_classdef = ClassDefinition(None, 'Object')
    _init_class_def_from_data(__object_classdef)
    add_builtin(__object_classdef.name, __object_classdef)
    
def _make_type(type_name):
    type_type = get_type('Type')
    typedef = TypeDefinition(type_type, type_name, typeobj=type_type)
    add_type(typedef.name, typedef)
    return typedef

_PRIMITIVE_OPERATION_FUNCTIONS = {
        '*': operator.mul,
        '/': operator.floordiv,
        '+': operator.add,
        '-': operator.sub
    }

def _make_primitive_op_method_def(operation):
    
    def callable_content():
        stack_frame = peek_stack_frame()
        selfobj = stack_frame.symbol_stack['self']
        other = stack_frame.symbol_stack['other']
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
    superclass = get_builtin('Object')
    classdef = ClassDefinition(None, 'String', superclass=superclass)
    
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
    superclass = get_builtin('Object')
    classdef = ClassDefinition(None, class_name, superclass=superclass)
    
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
    typedef = TypeDefinition(typedef_superobj, 'Nothing')
    typedef.set_typeobj(get_type('Type'))
    superobj = make_object()
    nothing_obj = ObjectDefinition(superobj, name='nothing')
    nothing_obj.set_typeobj(typedef)
    add_builtin(nothing_obj.name, nothing_obj)

def _make_boolean():
    typedef_superobj = make_object()
    typedef = TypeDefinition(typedef_superobj, 'Boolean')
    typedef.set_typeobj(get_type('Type'))
    add_type(typedef.name, typedef)
    
def _make_false():
    typedef = get_type('Boolean')
    superobj = make_object()
    false_obj = ObjectDefinition(superobj, name='false')
    false_obj.set_typeobj(typedef)
    add_builtin(false_obj.name, false_obj)
    
def _make_true():
    typedef = get_type('Boolean')
    superobj = make_object()
    true_obj = ObjectDefinition(superobj, name='true')
    true_obj.set_typeobj(typedef)
    add_builtin(true_obj.name, true_obj)

def _make_function_print():
    def fn_print():
        value = peek_stack_frame().symbol_stack['value'].to_lang_string()
        print(value.primitive)
    
    fn = Function('print', fn_print, 'value')
    add_builtin(fn.name, fn)
    
def _make_function_string():
    def fn_string():
        value = peek_stack_frame().symbol_stack['value'].to_lang_string()
        return value
    
    fn = Function('string', fn_string, 'value')
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
    _make_string_class()
    _make_nothing()
    _make_boolean()
    _make_false()
    _make_true()
    _make_function_print()
    _make_function_string()
    _make_function_log_debug()
    _make_function_log_info()
    _make_numeric_class('Integer', int)
    _make_numeric_class('Float', float)
    
