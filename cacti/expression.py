from cacti.runtime import *

__all__ = [ 'OperationExpression', 'ReferenceExpression', 'ValueExpression' ]

class Expression:
    def __call__(self):
        return self.eval()
    
    def eval(self):
        pass
    
class OperationExpression(Expression):
    def __init__(self, operand_expr, operator, *operation_expr_params):
        self.__operand_expr = operand_expr
        self.__operator = operator
        self.__operation_expr_params = operation_expr_params
        
    def eval(self):
        pass

class ReferenceExpression(Expression):
    def __init__(self, symbol):
        self.__symbol = symbol
    
    def eval(self):
        return peek_call_env().symbol_stack[self.__symbol]
    
class ValueExpression(Expression):
    def __init__(self, value):
        self.__value = value
        
    def eval(self):
        return self.__value