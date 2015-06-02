from cacti.runtime import *
from cacti.lang import *
from cacti.builtin import *
from cacti.ast import *

from copy import copy

initialize_builtins()
mainobj = make_main()
call_env = CallEnv(mainobj, mainobj.name)
push_call_env(call_env)

#print(make_string('foo')['id']['type']['name'])

# expr = PropertyExpression(ValueExpression(make_string('foo')), *['id', 'type', 'name'])
# print(expr())

sp = SymbolTable()
sp.add_symbol('y', ValueHolder(make_string('first y')))
st = SymbolTable()
st.add_symbol('x', ValueHolder(make_integer(5)))
sb = SymbolTable()
sb.add_symbol('z', ValueHolder(make_integer(10)))

ss = SymbolTableStack()
ss.push(sp)
ss.push(st)
ss.push(sb)

print(ss)

print(id(ss['x']))

ss2 = copy(ss)

print(ss2)

print(id(ss2['x']))
 
# #print(ss)

# ssc = copy(ss)
 
# #print(ssc)

# sp['y'] = make_string('next y')
# st['x'] = make_integer(6)
 
# print(ss)
# print(ssc)

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
