from cacti.runtime import *
from cacti.builtin import initialize_builtins, make_main, get_builtin, make_integer
from cacti.lang import Function, Method, MethodDefinition
from cacti.parse import parse_file, parse_string

import pprint
import logging
import sys

logging.basicConfig(level=logging.FATAL, format='%(asctime)s %(message)s')

def set_up_main_call_env():
    mainobj = make_main()
    call_env = CallEnv(mainobj, mainobj.name)
    push_call_env(call_env)

def main():
    logging.debug('main()')
    initialize_builtins()
    logging.debug('finished init()')
    set_up_main_call_env()
    logging.debug('finished env()')
    
    #ast = parse_string('class foo {}')
    #print(ast)
    #ast()
    
    ast = parse_file(sys.argv[1])
    #logging.debug('finished parse()')
    #print(ast)
    ast()
    #logging.debug('finished exec()')
    
if __name__ == '__main__':
    main()
