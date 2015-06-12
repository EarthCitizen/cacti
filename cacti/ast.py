import logging
import sys
from cacti.debug import get_logger
import cacti.exceptions as ce
from cacti.runtime import *
from cacti.lang import *
from cacti.builtin import get_builtin, make_class, make_object

__all__ = [
    'Block', 'OperationExpression', 'PropertyExpression', 'ReferenceExpression', 'ValueExpression',
    'AssignmentStatement', 'ClosureDeclarationStatement', 'MethodDefinitionDeclarationStatement',
    'FunctionDeclarationStatement', 'ReturnStatement', 'ValDeclarationStatement', 'VarDeclarationStatement',
    'PropertyFieldDeclaration', 'PropertyGetSetDeclaration', 'GetMethodDefinitionStatement', 'SetMethodDefinitionStatement'
    ]

class Evaluable:
    def __call__(self):
        error = None
        try:
            return self.eval()
        except ce.ExecutionError as err:
            error = err
        
        if error:
            raise ce.FatalError(error, self.source)
    
    def eval(self):
        pass
    
    def __getattr__(self, name):
        if name == 'source':
            if name in self.__dict__:
                return self.__dict__[name]
            else:
                return ''
        else:
            object.__getattribute__(self, name)
    
    #def __setattr__(self, name, value):
    #    if name == 'source':
    #        self.__dict__[name] = value
    #    else:
    #        super().__setattr__(name, value)
    
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
    def __init__(self, symbol, value_expr, target_expr=None):
        self.logger = get_logger(self)
        
        self.__target_expr = target_expr
        self.__symbol = symbol
        self.__value_expr = value_expr
        
    def eval(self):
        value = self.__value_expr()
        if self.__target_expr:
            target = self.__target_expr()
        else:
            target = peek_call_env().symbol_stack.peek()
        self.logger.debug("Assign {}[{}] the value {}".format(target.to_string(), repr(self.__symbol), value.to_string()))
        target[self.__symbol] = value
        return value
        
    def __repr__(self):
        kwargs = {
            'class_name': self.__class__.__name__,
            'symbol': self.__symbol,
            'value_expr': repr(self.__value_expr),
            'target_expr': repr(self.__target_expr)
        }
        return "{class_name}('{symbol}', {value_expr}, {target_expr})".format(**kwargs)
    
class ClassDeclarationStatement(Evaluable):
    def __init__(self, name, superclass_name, *parts):
        self.logger = get_logger(self)
        
        self.__name = name
        self.__superclass_name = superclass_name
        self.__parts = parts
        
        self.logger.debug("Create: name={}, superclass_name={}".format(self.__name, self.__superclass_name))
        
    def eval(self):
        self.logger.debug("Begin eval")
        klass = make_class(self.__name, self.__superclass_name)
        self.logger.debug("Made class: " + str(klass))
        
        for p in self.__parts:
            if isinstance(p, MethodDefinitionDeclarationStatement):
                klass.add_method_definition(p())
            elif isinstance(p, PropertyFieldDeclaration):
                klass.add_property_definition(p())
            elif isinstance(p, PropertyGetSetDeclaration):
                klass.add_property_definition(p())
            elif isinstance(p, ValDefinition):
                klass.add_val_definition(p)
            elif isinstance(p, VarDefinition):
                klass.add_var_definition(p)
        
        table = peek_call_env().symbol_stack.peek()
        table.add_symbol(self.__name, ConstantValueHolder(klass))
        return klass
    
    def __repr__(self):
        return "{}({}, {}, {})".format(self.__class__.__name__, repr(self.__name), repr(self.__superclass_name), repr(self.__parts))

class PropertyFieldDeclaration(Evaluable):
    def __init__(self, property_name, field_name):
        self.__property_name = property_name
        self.__field_name = field_name
        
    def eval(self):
        field_name = self.__field_name
        def get_field_value():
            call_env = peek_call_env()
            selfobj = call_env.owner
            return selfobj.field_table[field_name]
        get_field_callable = Callable(get_field_value)
        def set_field_value():
            call_env = peek_call_env()
            selfobj = call_env.owner
            value = call_env.symbol_stack['value']
            selfobj.field_table[field_name] = value
        set_field_callable = Callable(set_field_value, 'value')
        return PropertyDefinition(self.__property_name, get_field_callable, set_field_callable)
    
    def __repr__(self):
        return "{}({}, {})".format(self.__class__.__name__, repr(self.__property_name), repr(self.__field_name))
        
class GetMethodDefinitionStatement(Evaluable):
    def __init__(self, content):
        self.__content = content
        
    def eval(self):
        method_callable = Callable(self.__content)
        return MethodDefinition('get', method_callable)
        
    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, repr(self.__content))
        
class SetMethodDefinitionStatement(Evaluable):
    def __init__(self, content, param):
        self.__content = content
        self.__param = param
        
    def eval(self):
        method_callable = Callable(self.__content, self.__param)
        return MethodDefinition('set', method_callable)
        
    def __repr__(self):
        return "{}({}, {})".format(self.__class__.__name__, repr(self.__content), repr(self.__param))

class PropertyGetSetDeclaration(Evaluable):
    def __init__(self, property_name, get_def, set_def):
        self.__property_name = property_name
        self.__get_def = get_def
        self.__set_def = set_def
        
    def eval(self):
        prop_def = PropertyDefinition(self.__property_name)
        prop_def.set_getter_method_def(self.__get_def())
        prop_def.set_getter_method_def(self.__get_def())
        return prop_def

    def __repr__(self):
        return "{}({}, {}, {})".format(self.__class__.__name__, repr(self.__property_name), repr(self.__get_def), repr(self.__set_def))
        
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
        
class ReturnStatement(Evaluable):
    def __init__(self, value_expr):
        self.__value_expr = value_expr
        
    def eval(self):
        value = self.__value_expr()
        raise ce.ExitBlockException(value)
        
    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, repr(self.__value_expr))

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
        try:
            for e in self.__exprs:
                value = e()
        except ce.ExitBlockException as e:
            value = e.value
        
        return value
            
    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, repr(self.__exprs))
