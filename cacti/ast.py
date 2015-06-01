from cacti.runtime import *
from cacti.lang import *
from cacti.builtin import make_class, make_object

__all__ = [
    'Block', 'OperationExpression', 'PropertyExpression', 'ReferenceExpression', 'ValueExpression',
    'AssignmentStatement', 'ClosureDeclarationStatement', 'MethodDefinitionDeclarationStatement',
    'FunctionDeclarationStatement', 'ValDeclarationStatement', 'VarDeclarationStatement'
    ]

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
                    
class PropertyExpression(Evaluable):
    def __init__(self, obj_expr, *prop_names):
        assert 0 == len(list(filter(lambda e: not isinstance(e, str), prop_names)))
        self.__obj_expr = obj_expr
        self.__prop_names = prop_names
    
    def eval(self):
        value = self.__obj_expr()
        for p in self.__prop_names:
            value = value[p]
            
        return value
        
    def __repr__(self):
        return "{}({}, {})".format(
                    self.__class__.__name__,
                    repr(self.__obj_expr),
                    repr(self.__prop_names))
        
class ReferenceExpression(Evaluable):
    def __init__(self, symbol):
        self.__symbol = symbol
    
    def eval(self):
        return peek_call_env().symbol_stack[self.__symbol]
    
    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, repr(self.__symbol))
    
class ValueExpression(Evaluable):
    def __init__(self, value):
        assert isinstance(value, ObjectDefinition)
        self.__value = value
        
    def eval(self):
        return self.__value
    
    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, repr(self.__value))
        
class AssignmentStatement(Evaluable):
    def __init__(self, symbol, expr):
        self.__symbol = symbol
        self.__expr = expr
        
    def eval(self):
        value = self.__expr()
        table = peek_call_env().symbol_stack.peek()
        table[self.__symbol] = value
        return value
        
    def __repr__(self):
        return "{}('{}', {})".format(self.__class__.__name__, self.__symbol, repr(self.__expr))
    
class ClassDeclarationStatement(Evaluable):
    def __init__(self, name, *parts):
        self.__name = name
        self.__parts = parts
        
    def eval(self):
        klass = make_class(self.__name)
        
        for p in self.__parts:
            if isinstance(p, MethodDefinitionDeclarationStatement):
                klass.add_method_definition(p())
            elif isinstance(p, ValDefinition):
                klass.add_val_definition(p)
            elif isinstance(p, VarDefinition):
                klass.add_var_definition(p)
        
        table = peek_call_env().symbol_stack.peek()
        table.add_symbol(self.__name, ConstantValueHolder(klass))
        return klass
    
    def __repr__(self):
        return "{}({}, {})".format(self.__class__.__name__, repr(self.__name), repr(self.__parts))
        
class MethodDefinitionDeclarationStatement(Evaluable):
    def __init__(self, name, content, *params):
        self.__name = name
        self.__content = content
        self.__params = params
        
    def eval(self):
        method_callable = Callable(self.__content, *self.__params)
        return MethodDefinition(self.__name, method_callable)
        
    def __repr__(self):
        return "{}({}, {}, {})".format(self.__class__.__name__, repr(self.__name), repr(self.__content), repr(self.__params))

class ClosureDeclarationStatement(Evaluable):
    def __init__(self, expr, *params):
        self.__expr = expr
        self.__params = params
        
    def eval(self):
        kallable = Callable(self.__expr, *self.__params)
        call_env = peek_call_env()
        closure = Closure(call_env, kallable)
        return closure
        
    def __repr__(self):
        return "{}({}, {})".format(self.__class__.__name__, repr(self.__expr), repr(self.__params))

class FunctionDeclarationStatement(Evaluable):
    def __init__(self, name, expr, *params):
        self.__name = name
        self.__expr = expr
        self.__params = params
        
    def eval(self):
        kallable = Callable(self.__expr, *self.__params)
        function = Function(self.__name, kallable)
        call_env = peek_call_env()
        if self.__name:
            table = call_env.symbol_stack.peek()
            table.add_symbol(self.__name, ConstantValueHolder(function))
        
        return function
        
    def __repr__(self):
        return "{}({}, {}, {})".format(self.__class__.__name__, repr(self.__name), repr(self.__expr), repr(self.__params))

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
        
    def __repr__(self):
        return "{}({}, {})".format(self.__class__.__name__, repr(self.__symbol), repr(self.__init_expr))

class VarDeclarationStatement(Evaluable):
    def __init__(self, symbol, init_expr):
        self.__symbol = symbol
        self.__init_expr = init_expr
        
    def eval(self):
        value = self.__init_expr()
        call_env = peek_call_env()
        table = call_env.symbol_stack.peek()
        table.add_symbol(self.__symbol, ValueHolder(value))
        return value
        
    def __repr__(self):
        return "{}('{}', {})".format(self.__class__.__name__, self.__symbol, repr(self.__init_expr))

class Block(Evaluable):
    def __init__(self, *exprs):
        self.__exprs = exprs

    def eval(self):
        value = None
        for e in self.__exprs:
            value = e()
        
        return value
            
    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, repr(self.__exprs))
