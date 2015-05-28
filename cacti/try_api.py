from cacti.runtime import *
from cacti.lang import *
from cacti.builtin import *

from copy import copy

initialize_builtins()

sp = SymbolTable()
sp.add_symbol('y', ValueHolder(make_string('first y')))
st = SymbolTable()
st.add_symbol('x', ValueHolder(make_integer(5)))

ss = SymbolTableStack()
ss.push(sp)
ss.push(st)
 
#print(ss)

ssc = copy(ss)
 
#print(ssc)

sp['y'] = make_string('next y')
st['x'] = make_integer(6)
 
print(ss)
print(ssc)

# v = ValueHolder(make_integer(5))
# 
# print(v)
# print(id(v.get_value()))
# 
# vc = copy(v)
# 
# print(id(vc.get_value()))
# 
# print(id(v))
# print(id(vc))

#v.set_value(6)

#print(v)
#print(vc)
