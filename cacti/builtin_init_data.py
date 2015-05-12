__all__ = [ 'BUILTIN_INIT_DATA', 'init_class_def_from_data', 'init_object_def_from_class_def']

from cacti.runtime import *
from cacti.lang import *

class StubCallable:
    def __init__(self, content):
        self.__content = content
    
    def call(self, *param_values):
        self.__content()

### HOOK NEW ###

def hook_new_body():
    class_def = peek_call_env().owner
    superclass_def = class_def.superclass
    superobj = superclass_def.hook_table['()'] if superclass_def else None
    obj = ObjectDefinition(superobj, typeobj=class_def)
    init_object_def_from_class_def(obj, class_def)
    
    if superobj:
        superobj.set_selfobj(obj)
    
    return obj
    
hook_new_callable = Callable(hook_new_body)

hook_new_def = MethodDefinition('()', hook_new_callable)

### HOOK PROPERTY OF ###

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
        
hook_property_of_def = MethodDefinition('.', hook_property_of_callable)

def make_method_def_op_not_supported(operation, *param_names):
    def do_raise():
        raise OperationNotSupportedError(operation)
    method_callable = StubCallable(do_raise)
    return MethodDefinition(operation, method_callable)
    
def debug_type():
     return peek_call_env().symbol_stack['self'].typeobj

BUILTIN_INIT_DATA = {
        'Object': {
                'superclass': None,
                
                'hooks': {
                        MethodDefinition('()', hook_new_callable)
                    },
                
                'hook_defs': {
                        MethodDefinition('.', hook_property_of_callable),
                        
                        make_method_def_op_not_supported('()'),
                        make_method_def_op_not_supported('[]'),
                        make_method_def_op_not_supported('*'),
                        make_method_def_op_not_supported('/'),
                        make_method_def_op_not_supported('+'),
                        make_method_def_op_not_supported('-'),
                        
                        make_method_def_op_not_supported('*='),
                        make_method_def_op_not_supported('/='),
                        make_method_def_op_not_supported('+='),
                        make_method_def_op_not_supported('-=')
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

def init_class_def_from_data(class_def):
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

        
def init_object_def_from_class_def(object_def, class_def):
    
    for hook_def in class_def.hook_definitions:
        object_def.add_hook(hook_def.name, hook_def.callable)
        
    for method_def in class_def.method_definitions:
        object_def.add_method(method_def.name, method_def.callable)
        
    for prop_def in class_def.property_definitions:
        object_def.add_property(prop_def.name, prop_def.getter_callable, prop_def.setter_callable)
        
    for val_def in class_def.val_definitions:
        object_def.add_val(val_def.name, val_def.init_expr)
        
    for var_def in class_def.var_definitions:
        object_def.add_var(var_def.name, var_def.init_expr)
        
    object_def.set_typeobj(class_def)
