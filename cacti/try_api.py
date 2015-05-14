from cacti.runtime import *
from cacti.lang import *
from cacti.builtin import *

__user_object = get_builtin('Object').hook_table['()'].call()

push_call_env(CallEnv(object(), 'main'))

print(__user_object.hook_table['.'].call('string'))

method_callable = Callable(lambda: 4 + 9)
method = Method(__user_object, 'foo', method_callable)
print(method)
print(method.hook_table['()'].call())

function_callable = Callable(lambda: 4 + 9)
function = Function('foo', function_callable)
print(function)
print(function.hook_table['()'].call())

closure_env = CallEnv(object(), 'something')
closure_env_symbols = SymbolTable()
closure_env_symbols.add_symbol('x', ConstantValueHolder(10))
closure_env_symbols.add_symbol('y', ConstantValueHolder(2))
closure_env.symbol_stack.push(closure_env_symbols)
def closure_content():
    call_env = peek_call_env()
    x = call_env.symbol_stack['x']
    y = call_env.symbol_stack['y']
    return x * y
closure_callable = Callable(closure_content)
closure = Closure(closure_env, closure_callable)
print(closure)
print(closure.hook_table['()'].call())

stringobj1 = get_builtin('String').hook_table['()'].call()
stringobj2 = get_builtin('String').hook_table['()'].call()
print(stringobj1)
stringobj1.hook_table['+'].call(5)
