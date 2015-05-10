__all__ = [ 'BUILTIN_INIT_DATA' 'init_class_def']

from cacti.runtime import *
from cacti.lang import *

def hook_property_of(property_name):
    call_owner = peek_call_env(1).owner
    curr_owner = peek_call_env().owner
    if call_owner is curr_owner:
        return curr_owner.private_table
    else:
        return curr_owner.public_table
        
hook_property_of_def = MethodDefinition('.', hook_property_of)

def make_method_def_op_not_supported(operation):
    def do_raise():
        raise OperationNotSupportedError(operation)
    return MethodDefinition(operation, do_raise)

BUILTIN_INIT_DATA = {
        'Object': {
                'hook_defs': {
                        MethodDefinition('.', hook_property_of),
                        
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
                        PropertyDefinition('string', getter_callable=lambda: str(peek_call_env().owner)),
                        PropertyDefinition('type',   getter_callable=lambda: peek_call_env().owner.type_def),
                        PropertyDefinition('name',   getter_callable=lambda: peek_call_env().owner.name),
                        PropertyDefinition('id',     getter_callable=lambda: id(peek_call_env().owner))
                    }
            }
    }

def init_class_def(class_def):
    object_dict = BUILTIN_INIT_DATA[class_def.name]
    hook_defs = object_dict['hook_defs']
    method_defs = object_dict['method_defs']
    property_defs = object_dict['property_defs']
    
    for hook_def in hook_defs:
        class_def.add_hook_definition(hook_def)
        
    for method_def in method_defs:
        class_def.add_method_definition(method_def)
    
    for property_def in property_defs:
        class_def.add_property_definition(property_def)