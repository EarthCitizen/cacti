__all__ = [
        # Exceptions
        'ArityError', 'ConstantValueError', 'OperationNotSupportedError', 'SymbolContentError', 'SymbolError', 'SymbolUnknownError',
    ]

class ArityError(Exception): pass

class ConstantValueError(Exception): pass

class UnsupportedMethodError(Exception): pass

class UnknownPropertyError(Exception): pass

class OperationNotSupportedError(Exception):
    def __init__(self, operation):
        super().__init__("Operation '{}' not supported".format(operation))

class SymbolError(Exception): pass

class SymbolContentError(SymbolError): pass

class SymbolUnknownError(SymbolError):
    def __init__(self, symbol_name):
        super().__init__("Unknown symbol '{}'".format(symbol_name))