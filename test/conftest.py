import pytest
from cacti.runtime import *
from cacti.builtin import *

@pytest.fixture
def set_up_env():
        call_env = CallEnv(make_object(), 'test')
        table = SymbolTable()
        call_env.symbol_stack.push(table)
        push_call_env(call_env)
