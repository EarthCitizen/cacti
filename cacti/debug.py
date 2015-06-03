import logging
import traceback

__all__ = ['get_logger', 'print_stack_trace']

def get_logger(o):
    return logging.getLogger(o.__module__ + '.' + o.__class__.__name__)

def print_stack_trace():
    for line in traceback.format_stack():
        print(line)