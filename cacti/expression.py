from cacti.runtime import *

__all__ = [ 'OperationExpression', 'ReferenceExpression', 'ValueExpression' ]

class Expression:
    def __call__(self):
        return self.eval()
    
    def eval(self):
        pass
    
class OperationExpression(Expression):
    def __init__(self, operand_expr, operation, *operation_expr_params):
        self.__operand_expr = operand_expr
        self.__operation = operation
        self.__operation_expr_params = operation_expr_params
        
    def eval(self):
        target = self.__operand_expr()
        params = list(map(lambda e: e(), self.__operation_expr_params))
        return target.hook_table[self.__operation].call(*params)
        

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