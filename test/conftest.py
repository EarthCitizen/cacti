import pytest
from cacti.runtime import *
from cacti.builtin import *

initialize_builtins()

@pytest.fixture
def set_up_env():
        stack_frame = StackFrame(make_object(), 'test')
        table = SymbolTable()
        stack_frame.symbol_stack.push(table)
        push_stack_frame(stack_frame)
