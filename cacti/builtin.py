from cacti.runtime import *
from cacti.lang import *
from cacti.builtin_init_data import *

BUILTIN_SYMBOLS = SymbolTable()

def add_builtin(symbol_name, object_instance):
    BUILTIN_SYMBOLS.add_symbol(symbol_name, ConstantValueHolder(object_instance))

__object = ObjectDefinition(None)
__object_classdef = ClassDefinition(__object, 'Object')
init_class_def_from_data(__object_classdef)
init_object_def_from_class_def(__object, __object_classdef)

__classdef_typedef_superobj =  __object_classdef.hook_table['()'].call()

__typedef_typedef = ObjectDefinition(__object, name='TypeDefinition')

__object.set_type_def(__object_classdef)
__object_classdef.set_type_def(__typedef_typedef)
__typedef_typedef.set_type_def(__typedef_typedef)

#__function_typedef = ObjectDefinition(__object, name='Function', type_def=__object_typedef)
#__method_typedef = ObjectDefinition(__object, name='Method', type_def=__object_typedef)

add_builtin(__object_classdef.name, __object_classdef)
add_builtin(__typedef_typedef.name, __typedef_typedef)
#add_builtin(__object_typedef.name, __object_typedef)
#add_builtin(__method_typedef.name, __method_typedef)

print(__classdef_typedef_superobj.type_def)

print(__object)
print(__object_classdef)
print(__object_classdef.hook_table['()'].call().type_def.name)
#print(__object.property_table['string'].call())
#print(__object.property_table['type'])
#print(__object.property_table['string'])
#print(__object.property_table['name'])
#print(__object.type_def)
#print(__object.type_def.name)
#print(__object.type_def.type_def.name)

# object.type.name => Object
# object.type.to_string => Class<Object>
# object.type.type.name => Class
# object.type.type.to_string => Type<Class>
# object.type.type.type.name => Type
# object.type.type.type.to_string => Type<Type>