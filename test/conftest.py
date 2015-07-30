import pytest
from cacti.runtime import *
from cacti.builtin import *

initialize_builtins()

@pytest.fixture
def set_up_env():
        call_env = StackFrame(make_object(), 'test')
        table = SymbolTable()
        call_env.symbol_stack.push(table)
        push_stack_frame(call_env)
