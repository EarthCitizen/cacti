from cacti.runtime import *
from cacti.builtin import initialize_builtins, make_main, get_builtin, make_integer
from cacti.lang import Function, Method, MethodDefinition
from cacti.parse import parse_file, parse_string

import pprint

def set_up_main_call_env():
    mainobj = make_main()
    call_env = CallEnv(mainobj, mainobj.name)
    push_call_env(call_env)

def main():
    initialize_builtins()
    set_up_main_call_env()
    
    #ast = parse_string('print("Hello World!")')
    #ast()
    
    ast = parse_file('examples/test.cacti')
    ast()
    
if __name__ == '__main__':
    main()
