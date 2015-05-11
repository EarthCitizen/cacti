from cacti.runtime import *
from cacti.lang import *
from cacti.builtin_init_data import *

BUILTIN_SYMBOLS = SymbolTable()

def add_builtin(symbol_name, object_instance):
    BUILTIN_SYMBOLS.add_symbol(symbol_name, ConstantValueHolder(object_instance))

__object_classdef_superobj = ObjectDefinition(None)
__object_classdef = ClassDefinition(__object_classdef_superobj, 'Object')
__object_classdef_superobj.set_selfobj(__object_classdef)
init_class_def_from_data(__object_classdef)
init_object_def_from_class_def(__object_classdef_superobj, __object_classdef)

__typedef_typedef_superobj = __object_classdef.hook_table['()'].call()
__typedef_typedef = TypeDefinition(__typedef_typedef_superobj, 'Type')
__typedef_typedef_superobj.set_selfobj(__typedef_typedef)
__typedef_typedef.set_typeobj(__typedef_typedef)

__classdef_typedef_superobj = __object_classdef.hook_table['()'].call()
__classdef_typedef = TypeDefinition(__classdef_typedef_superobj, 'Class')
__classdef_typedef_superobj.set_selfobj(__classdef_typedef)
__classdef_typedef.set_typeobj(__typedef_typedef)

__object_classdef.set_typeobj(__classdef_typedef)

__user_object = __object_classdef.hook_table['()'].call()

#### WHERE TO LOAD IN NAME PROPERTY???

print(__user_object.property_table['type'])
print(__user_object.property_table['type'].property_table['type'])
print(__user_object.property_table['type'].property_table['type'].property_table['type'])
# SUPER.SUPER is broken, it keeps returning the same objet, instead of going up
print(__user_object.property_table['type'].property_table['super'])
print(__user_object.property_table['type'].property_table['super'].property_table['super'])