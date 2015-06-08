import inspect
import logging
import traceback

__all__ = ['configure_logging', 'get_logger', 'print_stack_trace']

__format = '%(levelname)s | %(file_line)-20s | %(name_fun)-45s >> %(env_info)s: %(message)s'

def configure_logging():
    logging.basicConfig(level=logging.FATAL, format=__format)
    old_factory = logging.getLogRecordFactory()
    def record_factory(*args, **kwargs):
        from cacti.runtime import peek_call_env
        record = old_factory(*args, **kwargs)
        call_env = peek_call_env()
        env_info = "{}('{}')".format(call_env.owner.to_string(), call_env.name)
        record.env_info = env_info
        record.file_line = record.filename + ':' + str(record.lineno)
        record.name_fun = "{}:{}".format(record.name, record.funcName)
        return record
    logging.setLogRecordFactory(record_factory)

def get_logger(o):
    if isinstance(o, str):
        logger_name = o
    elif inspect.isfunction(o):
        logger_name = o.__module__ + '.' + o.__name__
    else:
        logger_name = o.__module__ + '.' + o.__class__.__name__
    return logging.getLogger(logger_name)

def print_stack_trace():
    for line in traceback.format_stack():
        print(line)