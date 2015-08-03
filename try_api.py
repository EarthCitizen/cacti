from cacti.runtime import *
from cacti.lang import *
from cacti.builtin import *
from cacti.ast import *

from copy import copy

initialize_builtins()
mainobj = make_main()
stack_frame = StackFrame(mainobj, mainobj.name)
push_stack_frame(stack_frame)

#print(get_type('Class').typeobj.typeobj.name)
#print(get_type('Class').typeobj.to_repr())
#print(get_type('Class').typeobj.to_string())
#print(get_type('Class').typeobj.to_native_repr())

i = get_builtin('Integer')

#print(get_builtin('Integer').to_string())
#print(get_builtin('Integer').typeobj.to_string())
#print(i.typeobj.typeobj.to_string())
#print(i.property_table['type'].property_table['type'].to_string())
#print(i.selfobj['type'].selfobj['type'].to_string())

t1 = i
print("{}<'{}'>".format(t1.selfobj.typeobj.name, t1.selfobj.name))
t2 = t1.typeobj
print("{}<'{}'>".format(t2.selfobj.typeobj.name, t2.selfobj.name))
t3 = t2.typeobj
print("{}<'{}'>".format(t3.selfobj.typeobj.name, t3.selfobj.name))
t4 = t3.typeobj
print("{}<'{}'>".format(t4.selfobj.typeobj.name, t4.selfobj.name))
print(repr(t4))
print(t4.typeobj.name)
print(t4.selfobj.typeobj.name)
#print(get_builtin('Integer').typeobj.typeobj.typeobj.to_string())



