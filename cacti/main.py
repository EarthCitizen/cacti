from cacti.runtime import *
from cacti.builtin import initialize_builtins, make_main, get_builtin, make_integer
from cacti.debug import configure_logging
from cacti.lang import Function, Method, MethodDefinition
from cacti.parse import parse_module_file, parse_string

import pprint
import logging
import sys

#logging.basicConfig(level=logging.FATAL)#, format='%(levelname)s | %(filename)s:%(lineno)d | %(name)s.%(funcName)s: %(message)s')
#logging.getLogger().setLevel(logging.INFO)

configure_logging()

#def set_up_main_stack_frame():
#    mainobj = make_main()
#    stack_frame = StackFrame(mainobj, mainobj.name)
#    push_stack_frame(stack_frame)

def main():
    initialize_runtime()
    initialize_builtins()
    #set_up_main_stack_frame()
    
    #ast = parse_string('class foo {}')
    #print(ast)
    #ast()
    
    module_declaration = parse_module_file(sys.argv[1])
    #ast = parse_file('/Users/ryan/Dropbox/repositories/cacti/examples/class.cacti')
    logging.debug('finished parse()')
    #print(module_declaration)
    module_declaration()
    m = get_module('some.test.module')
    print(m.name)
    #logging.debug('finished exec()')
    #i = make_integer(7)
    #print('=======')
    #print(i.typeobj.to_string())
    
if __name__ == '__main__':
    main()
