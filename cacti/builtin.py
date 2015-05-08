from cacti.runtime import *
from cacti.lang import *

#BUILTIN_SYMBOLS = SymbolTable()

#def add_builtin(symbol_name, object_instance):
#    BUILTIN_SYMBOLS.add_symbol(symbol_name, ConstantValueHolder(object_instance))

__object = ObjectDefinition.__new__(ObjectDefinition)
__object_typedef = TypeDefinition.__new__(TypeDefinition)
__typedef_typedef = TypeDefinition.__new__(TypeDefinition)

__object.__init__(__object_typedef, None)
__typedef_typedef.__init__(__typedef_typedef, __object, 'TypeDefinition')
__object_typedef.__init__(__typedef_typedef, __object, 'Object')

__function_typedef = TypeDefinition(__object_typedef, __object, 'Function')
__method_typedef = TypeDefinition(__object_typedef, __object, 'Method')

add_builtin(__object_typedef.name, __object_typedef)
add_builtin(__typedef_typedef.name, __typedef_typedef)
add_builtin(__object_typedef.name, __object_typedef)
add_builtin(__method_typedef.name, __method_typedef)


#print(__object.type_def.type_def.name)

# object.type.name => Object
# object.type.type.name => TypeDefinition