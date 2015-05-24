from cacti.runtime import *
from cacti.builtin import make_main
from cacti.lang import Function, Method, MethodDefinition

def set_up_main_call_env():
    mainobj = make_main()
    call_env = CallEnv(mainobj, mainobj.name)
    table = SymbolTable()
    call_env.symbol_stack.push(table)
    push_call_env(call_env)

def main():
    set_up_main_call_env()
    
    
if __name__ == '__main__':
    main()
