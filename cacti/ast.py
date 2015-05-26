from cacti.runtime import *

__all__ = [ 'Block', 'OperationExpression', 'ReferenceExpression', 'ValueExpression', 'ValDeclarationStatement' ]

class Evaluable:
    def __call__(self):
        return self.eval()
    
    def eval(self):
        pass
    
class OperationExpression(Evaluable):
    def __init__(self, operand_expr, operation, *operation_expr_params):
        self.__operand_expr = operand_expr
        self.__operation = operation
        self.__operation_expr_params = operation_expr_params
        
    def eval(self):
        target = self.__operand_expr()
        params = list(map(lambda e: e(), self.__operation_expr_params))
        return target.hook_table[self.__operation].call(*params)
    
    def __repr__(self):
        return "{}({}, '{}', {})".format(
                    self.__class__.__name__,
                    repr(self.__operand_expr),
                    self.__operation,
                    repr(self.__operation_expr_params))
        
class ReferenceExpression(Evaluable):
    def __init__(self, symbol):
        self.__symbol = symbol
    
    def eval(self):
        return peek_call_env().symbol_stack[self.__symbol]
    
    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, repr(self.__symbol))
    
class ValueExpression(Evaluable):
    def __init__(self, value):
        self.__value = value
        
    def eval(self):
        return self.__value
    
    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, repr(self.__value))

class ValDeclarationStatement(Evaluable):
    def __init__(self, symbol, init_expr):
        self.__symbol = symbol
        self.__init_expr = init_expr
        
    def eval(self):
        value = self.__init_expr()
        call_env = peek_call_env()
        table = call_env.symbol_stack.peek()
        table.add_symbol(self.__symbol, ConstantValueHolder(value))
        return value
    
class Block(Evaluable):
    def __init__(self, *exprs):
        self.__exprs = exprs

    def eval(self):
        for e in self.__exprs:
            e()
