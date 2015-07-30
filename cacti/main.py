from cacti.runtime import *
from cacti.builtin import initialize_builtins, make_main, get_builtin, make_integer
from cacti.debug import configure_logging
from cacti.lang import Function, Method, MethodDefinition
from cacti.parse import parse_file, parse_string

import pprint
import logging
import sys

#logging.basicConfig(level=logging.FATAL)#, format='%(levelname)s | %(filename)s:%(lineno)d | %(name)s.%(funcName)s: %(message)s')
#logging.getLogger().setLevel(logging.INFO)

configure_logging()

def set_up_main_call_env():
    mainobj = make_main()
    call_env = StackFrame(mainobj, mainobj.name)
    push_stack_frame(call_env)

def main():
    initialize_builtins()
    set_up_main_call_env()
    
    #ast = parse_string('class foo {}')
    #print(ast)
    #ast()
    
    ast = parse_file(sys.argv[1])
    #ast = parse_file('/Users/ryan/Dropbox/repositories/cacti/examples/class.cacti')
    logging.debug('finished parse()')
    #print(ast)
    ast()
    #logging.debug('finished exec()')
    #i = make_integer(7)
    #print('=======')
    #print(i.typeobj.to_string())
    
if __name__ == '__main__':
    main()
