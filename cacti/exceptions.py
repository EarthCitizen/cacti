__all__ = [
        # Exceptions
        'ArityError', 'ConstantValueError', 'OperationNotSupportedError',
        'ExecutionError', 'FatalError',
        'SymbolContentError', 'SymbolError', 'SymbolUnknownError', 'SyntaxError'
    ]

class ExecutionError(Exception): pass
   
class ArityError(ExecutionError): pass

class ConstantValueError(ExecutionError): pass

class UnsupportedMethodError(ExecutionError): pass

class UnknownPropertyError(ExecutionError): pass

class OperationNotSupportedError(ExecutionError):
    def __init__(self, name, operation):
        super().__init__("Operation '{}' not supported for '{}'".format(operation, name))
        
class FatalError(Exception):
    def __init__(self, cause, source):
        super().__init__("{} at: {}".format(cause.__class__.__name__, source))

class SymbolError(ExecutionError): pass

class SymbolContentError(SymbolError): pass

class SymbolUnknownError(SymbolError):
    def __init__(self, symbol_name):
        super().__init__("Unknown symbol '{}'".format(symbol_name))
        
class SyntaxError(Exception): pass