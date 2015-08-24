__all__ = [
        # Exceptions
        'ArityError', 'ConstantValueError', 'InvalidTypeError', 'OperationNotSupportedError',
        'ExecutionError', 'FatalError',
        'SymbolContentError', 'SymbolError', 'SymbolUnknownError', 'SyntaxError'
    ]
    
class ExecutionError(Exception): pass
   
class ArityError(ExecutionError): pass

class ConstantValueError(ExecutionError): pass

class InvalidTypeError(ExecutionError): pass

class UnsupportedMethodError(ExecutionError): pass

class UnknownPropertyError(ExecutionError): pass

class OperationNotSupportedError(ExecutionError):
    def __init__(self, name, operation):
        super().__init__("Operation '{}' not supported for '{}'".format(operation, name))
        
class FatalError(Exception):
    def __init__(self, cause, source):
        cause_class_name = cause.__class__.__name__
        source_ref = source.strip()
        cause_message = str(cause)
        if 0 == len(cause_message):
            error_message = "{} at: {}".format(cause_class_name, source_ref)
        else:
            error_message = "{}({}) at: {}".format(cause_class_name, cause_message, source_ref)
        super().__init__(error_message)

class SymbolError(ExecutionError): pass

class SymbolContentError(SymbolError): pass

class SymbolUnknownError(SymbolError):
    def __init__(self, symbol_name):
        super().__init__("Unknown symbol '{}'".format(symbol_name))
        
class SyntaxError(Exception):
    def __init__(self, s, loc, message):
        from pyparsing import col, line, lineno
        kwargs = {
            'message': message,
            'line': str(lineno(loc, s)),
            'column': str(col(loc, s)),
            'source': line(loc, s).strip()
        }
        m = '{}: {}:{}: {}'.format(**kwargs)
        super().__init__(m)
        