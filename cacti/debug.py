import traceback

__all__ = ['print_stack_trace']

def print_stack_trace():
    for line in traceback.format_stack():
        print(line)