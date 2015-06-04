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
        record.name_fun = "{}.{}".format(record.name, record.funcName)
        return record
    logging.setLogRecordFactory(record_factory)


class _CallEnvAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        #self.extra['foo'] = 123
        print(">>" + str(self.extra))
        return super().process("FOO:" + msg, kwargs)

def get_logger(o):
    return logging.getLogger(o.__module__ + '.' + o.__class__.__name__)
    #return _CallEnvAdapter(logger, {'foo': 123})

def print_stack_trace():
    for line in traceback.format_stack():
        print(line)