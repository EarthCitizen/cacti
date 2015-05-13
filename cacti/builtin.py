from cacti.runtime import *
from cacti.lang import *
from cacti.exceptions import *

__all__ = ['get_type', 'get_builtin']

class _StubCallable:
    def __init__(self, content):
        self.__content = content
    
    def call(self, *param_values):
        self.__content()

### HOOK NEW ###
def _hook_new_callable_content():
    class_def = peek_call_env().owner
    superclass_def = class_def.superclass
    superobj = superclass_def.hook_table['()'].call() if superclass_def else None
    obj = ObjectDefinition(superobj, typeobj=class_def)
    _init_object_def_from_class_def(obj, class_def)
    
    return obj

def _make_hook_new_method_def():
    def hook_new_body():
        class_def = peek_call_env().owner
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
        call_owner = peek_call_env(1).owner
        curr_env = peek_call_env()
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
        call_env = peek_call_env()
        raise OperationNotSupportedError(call_env.owner.selfobj.typeobj.name, call_env.name)
    method_callable = _StubCallable(do_raise)
    return MethodDefinition(operation, method_callable)
    
BUILTIN_INIT_DATA = {
        'Object': {
                'superclass': None,
                
                'hooks': {
                        _make_hook_new_method_def()
                    },
                
                'hook_defs': {
                        _make_hook_property_of_method_def(),
                        
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
                        PropertyDefinition('string', getter_callable=Callable(lambda: str(peek_call_env().symbol_stack['self']))),
                        PropertyDefinition('type',   getter_callable=Callable(lambda: peek_call_env().symbol_stack['self'].typeobj)),
                        PropertyDefinition('id',     getter_callable=Callable(lambda: id(peek_call_env().symbol_stack['self'])))
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
        class_def.add_hook(hook.name, hook.callable)
    
    for hook_def in hook_defs:
        class_def.add_hook_definition(hook_def)
        
    for method_def in method_defs:
        class_def.add_method_definition(method_def)
    
    for property_def in property_defs:
        class_def.add_property_definition(property_def)

        
def _init_object_def_from_class_def(object_def, class_def):
    
    for hook_def in class_def.hook_definitions:
        object_def.add_hook(hook_def.name, hook_def.callable)
        
    for method_def in class_def.method_definitions:
        object_def.add_method(method_def.name, method_def.callable)
        
    for prop_def in class_def.property_definitions:
        object_def.add_property(prop_def.name, prop_def.getter_callable, prop_def.setter_callable)
        
    # Initialize constants
    for val_def in class_def.val_definitions:
        object_def.add_val(val_def.name, val_def.init_expr())
        
    # Initialize vars after constants
    for var_def in class_def.var_definitions:
        object_def.add_var(var_def.name, var_def.init_expr())
        
    object_def.set_typeobj(class_def)

_TYPES = SymbolTable()
_BUILTINS = SymbolTable()

def add_type(symbol_name, object_instance):
    _TYPES.add_symbol(symbol_name, ConstantValueHolder(object_instance))
    
def get_type(symbol_name):
    return _TYPES[symbol_name]

def add_builtin(symbol_name, object_instance):
    _BUILTINS.add_symbol(symbol_name, ConstantValueHolder(object_instance))
    
def get_builtin(symbol_name):
    return _BUILTINS[symbol_name]

def _bootstrap_basic_types():
    # BOOTSTRAP THE CLASS DEFINITION FOR Object
    __object_classdef_superobj = ObjectDefinition(None)
    __object_classdef = ClassDefinition(__object_classdef_superobj, 'Object')
    _init_class_def_from_data(__object_classdef)
    _init_object_def_from_class_def(__object_classdef_superobj, __object_classdef)
    
    __typedef_typedef_superobj = __object_classdef.hook_table['()'].call()
    __typedef_typedef = TypeDefinition(__typedef_typedef_superobj, 'Type')
    __typedef_typedef.set_typeobj(__typedef_typedef)
    
    __classdef_typedef_superobj = __object_classdef.hook_table['()'].call()
    __classdef_typedef = TypeDefinition(__classdef_typedef_superobj, 'Class')
    __classdef_typedef.set_typeobj(__typedef_typedef)
    
    __object_classdef.set_typeobj(__classdef_typedef)
    
    add_builtin(__object_classdef.name, __object_classdef)
    
    add_type(__typedef_typedef.name, __typedef_typedef)
    add_type(__classdef_typedef.name, __classdef_typedef)
    
def _make_type(type_name):
    superobj = get_builtin('Object').hook_table['()'].call()
    typedef = TypeDefinition(superobj, type_name)
    typedef.set_typeobj(get_type('Type'))
    add_type(typedef.name, typedef)

_bootstrap_basic_types()
_make_type('Function')
_make_type('Closure')
_make_type('Method')

def _make_string_class():
    superobj = get_builtin('Object').hook_table['()'].call()
    typeobj = get_type('Class')
    superclass = get_builtin('Object')
    string_classdef = ClassDefinition(superobj, 'String', typeobj=typeobj, superclass=superclass)
    
    def string_new_callable_content():
        obj = _hook_new_callable_content()
        obj.internal_table.add_symbol('primitive', ConstantValueHolder(''))
        return obj
        
    string_classdef.add_hook('()', Callable(string_new_callable_content))
    
    add_builtin('String', string_classdef)
    
_make_string_class()
