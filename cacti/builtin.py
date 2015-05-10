from cacti.runtime import *
from cacti.lang import *
from cacti.builtin_init_data import *

BUILTIN_SYMBOLS = SymbolTable()

def add_builtin(symbol_name, object_instance):
    BUILTIN_SYMBOLS.add_symbol(symbol_name, ConstantValueHolder(object_instance))

#__object = ObjectDefinition.__new__(ObjectDefinition)
#__object_typedef = TypeDefinition.__new__(TypeDefinition)
#__typedef_typedef = TypeDefinition.__new__(TypeDefinition)

# __object.__init__(__object_typedef, None)
# __typedef_typedef.__init__(__typedef_typedef, __object, 'TypeDefinition')
# __object_typedef.__init__(__typedef_typedef, __object, 'Object')

# __function_typedef = TypeDefinition(__object_typedef, __object, 'Function')
# __method_typedef = TypeDefinition(__object_typedef, __object, 'Method')


def init_object_class_def(class_def):
    object_dict = BUILTIN_INIT_DATA['Object']
    

__object = ObjectDefinition(None)
__object_classdef = ClassDefinition(__object, name='Object')
__typedef_typedef = ObjectDefinition(__object, name='TypeDefinition')

__object.set_type_def(__object_typedef)
__object_typedef.set_type_def(__typedef_typedef)
__typedef_typedef.set_type_def(__typedef_typedef)

__function_typedef = ObjectDefinition(__object, name='Function', type_def=__object_typedef)
__method_typedef = ObjectDefinition(__object, name='Method', type_def=__object_typedef)

add_builtin(__object_typedef.name, __object_typedef)
add_builtin(__typedef_typedef.name, __typedef_typedef)
add_builtin(__object_typedef.name, __object_typedef)
add_builtin(__method_typedef.name, __method_typedef)

print(__object)
print(__object.type_def)
print(__object.type_def.name)
print(__object.type_def.type_def.name)

# object.type.name => Object
# object.type.to_string => Class<Object>
# object.type.type.name => Class
# object.type.type.to_string => Type<Class>
# object.type.type.type.name => Type
# object.type.type.type.to_string => Type<Type>