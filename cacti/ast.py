import logging
import sys
from cacti.debug import get_logger
import cacti.exceptions as ce
from cacti.runtime import *
from cacti.lang import *
from cacti.builtin import get_builtin, make_class, make_object

__all__ = [
    'AssignmentStatement',
    'Block',
    'ClosureDeclarationStatement',
    'ExportStatement',
    'FunctionDeclarationStatement',
    'GetMethodDefinitionStatement',
    'ImportStatement',
    'MethodDefinitionDeclarationStatement',
    'ModuleDeclaration',
    'OperationExpression',
    'PropertyExpression',
    'PropertyFieldDeclaration',
    'PropertyGetSetDeclaration',
    'ReferenceExpression',
    'ReturnStatement',
    'SetMethodDefinitionStatement',
    'ValDeclarationStatement',
    'ValueExpression',
    'VarDeclarationStatement'
    ]

# Turn an iterable into a string
# with each element separated by
# a comma and space
def repr_comma_list(c):
    return ', '.join(list(map(repr, c)))

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

class ModuleDeclaration(Evaluable):
    def __init__(self, module_name, *statements):
        self.__module_name = module_name
        self.__statements = statements

    def eval(self):
        stack_frame = StackFrame(make_object(), self.__module_name)
        push_stack_frame(stack_frame)
        self.__execute_statements()
        module = Module(self.__module_name)
        self.process_statement_results(module, stack_frame)
        self.process_exports(module, stack_frame)
        pop_stack_frame()
        # TODO - we will eventuall need to
        # raise an error in some way and test
        # for that in the case that a module
        # already exists
        add_module(module)
        return module

    def __execute_statements(self):
        for statement in self.__statements:
            statement()

    def process_statement_results(self, module, stack_frame):
        # There should only be one item
        # in the symbol stack at this point.
        # If not, we have a problem.
        symbol_table = stack_frame.symbol_stack.peek()
        for k, v in symbol_table.symbol_holder_iter():
            module.private_table.add_symbol(k, v)

    def process_exports(self, module, stack_frame):
        data_store = stack_frame.data_store
        exports = data_store['exports'] if 'exports' in data_store else []
        symbol_holders = module.private_table.symbol_holder_iter()
        to_add = filter(lambda sh: sh[0] in exports, symbol_holders)
        for s, h in to_add:
            module.public_table.add_symbol(s, ConstantWrapperValueHolder(h))

    def __repr__(self):
        return "{}('{}', {})".format(
                    self.__class__.__name__,
                    self.__module_name,
                    repr_comma_list(self.__statements))
    
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
        return peek_stack_frame().symbol_stack[self.__symbol]
    
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
            target = peek_stack_frame().symbol_stack.peek()
        self.logger.debug("{}[{}] contains the value {}".format(target.to_string(), repr(self.__symbol), target[self.__symbol]))
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

class ExportStatement(Evaluable):
    def __init__(self, *exports):
        self.logger = get_logger(self)
        self.__exports = set(exports)

    def eval(self):
        peek_stack_frame().data_store['exports'] = set(self.__exports)
        return None

    def __repr__(self):
        kwargs = {
            'class_name': self.__class__.__name__,
            'exports': repr_comma_list(self.__exports)
        }
        return "{class_name}({exports})".format(**kwargs)

class ImportStatement(Evaluable):
    def __init__(self, module_name, *, alias=None, only=[]):
        self.logger = get_logger(self)
        self.__module_name = module_name
        self.__alias = alias
        self.__only = only

    def eval(self):
        table = peek_stack_frame().symbol_stack.peek()
        module = get_module(self.__module_name)
        if self.__alias:
            module_alias = ModuleAlias(module, *self.__only)
            table.add_symbol(self.__alias, ConstantValueHolder(module_alias))
        else:
            symbol_holders = module.public_table.symbol_holder_iter()
            if self.__only:
                symbol_holders = filter(lambda e: e[0] in self.__only, symbol_holders)
            for s, h in symbol_holders:
                table.add_symbol(s, h)

        return None

    def __repr__(self):
        kwargs = {
            'class_name': self.__class__.__name__,
            'module_name': repr(self.__module_name),
            'alias': repr(self.__alias),
            'only': repr(self.__only)
        }
        return "{class_name}({module_name}, alias={alias}, only={only})".format(**kwargs)

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
        
        table = peek_stack_frame().symbol_stack.peek()
        table.add_symbol(self.__name, ConstantValueHolder(klass))
        return klass
    
    def __repr__(self):
        return "{}({}, {}, {})".format(
                    self.__class__.__name__,
                    repr(self.__name),
                    repr(self.__superclass_name),
                    repr(self.__parts))

class PropertyFieldDeclaration(Evaluable):
    def __init__(self, property_name, field_name):
        self.__property_name = property_name
        self.__field_name = field_name
        
    def eval(self):
        field_name = self.__field_name
        def get_field_value():
            stack_frame = peek_stack_frame()
            selfobj = stack_frame.owner
            return selfobj.field_table[field_name]
        get_field_mdef = MethodDefinition('get', get_field_value)
        def set_field_value():
            stack_frame = peek_stack_frame()
            selfobj = stack_frame.owner
            value = stack_frame.symbol_stack['value']
            selfobj.field_table[field_name] = value
        set_field_mdef = MethodDefinition('set', set_field_value, 'value')
        return PropertyDefinition(self.__property_name, get_field_mdef, set_field_mdef)
    
    def __repr__(self):
        return "{}({}, {})".format(self.__class__.__name__, repr(self.__property_name), repr(self.__field_name))
        
class GetMethodDefinitionStatement(Evaluable):
    def __init__(self, content):
        self.__content = content
        
    def eval(self):
        return MethodDefinition('get', self.__content)
        
    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, repr(self.__content))
        
class SetMethodDefinitionStatement(Evaluable):
    def __init__(self, content, param):
        self.__content = content
        self.__param = param
        
    def eval(self):
        return MethodDefinition('set', self.__content, self.__param)
        
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
        set_def = self.__set_def() if self.__set_def else None
        prop_def.set_setter_method_def(set_def)
        return prop_def

    def __repr__(self):
        return "{}({}, {}, {})".format(
                    self.__class__.__name__,
                    repr(self.__property_name),
                    repr(self.__get_def), repr(self.__set_def))
        
class MethodDefinitionDeclarationStatement(Evaluable):
    def __init__(self, name, content, *params):
        self.__name = name
        self.__content = content
        self.__params = params
        
    def eval(self):
        return MethodDefinition(self.__name, self.__content, *self.__params)
        
    def __repr__(self):
        return "{}({}, {}, {})".format(
                    self.__class__.__name__,
                    repr(self.__name),
                    repr(self.__content),
                    repr(self.__params))

class ClosureDeclarationStatement(Evaluable):
    def __init__(self, expr, *params):
        self.__expr = expr
        self.__params = params
        
    def eval(self):
        stack_frame = peek_stack_frame()
        closure = Closure(stack_frame, self.__expr, *self.__params)
        return closure
        
    def __repr__(self):
        return "{}({}, {})".format(self.__class__.__name__, repr(self.__expr), repr(self.__params))

class FunctionDeclarationStatement(Evaluable):
    def __init__(self, name, expr, *params):
        self.__name = name
        self.__expr = expr
        self.__params = params
        
    def eval(self):
        function = Function(self.__name, self.__expr, *self.__params)
        stack_frame = peek_stack_frame()
        if self.__name:
            table = stack_frame.symbol_stack.peek()
            table.add_symbol(self.__name, ConstantValueHolder(function))
        
        return function
        
    def __repr__(self):
        return "{}({}, {}, {})".format(self.__class__.__name__, repr(self.__name), repr(self.__expr), repr(self.__params))
        
class ReturnStatement(Evaluable):
    def __init__(self, value_expr):
        self.__value_expr = value_expr
        
    def eval(self):
        value = self.__value_expr()
        peek_stack_frame().mark_exit_flag()
        return value
        
    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, repr(self.__value_expr))

class ValDeclarationStatement(Evaluable):
    def __init__(self, symbol, init_expr):
        self.__symbol = symbol
        self.__init_expr = init_expr
        
    def eval(self):
        value = self.__init_expr()
        stack_frame = peek_stack_frame()
        table = stack_frame.symbol_stack.peek()
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
        stack_frame = peek_stack_frame()
        table = stack_frame.symbol_stack.peek()
        table.add_symbol(self.__symbol, ValueHolder(value))
        return value
        
    def __repr__(self):
        return "{}('{}', {})".format(self.__class__.__name__, self.__symbol, repr(self.__init_expr))

class Block(Evaluable):
    def __init__(self, *exprs):
        self.__exprs = exprs

    def eval(self):
        value = None
        stack_frame = peek_stack_frame()
        
        for e in self.__exprs:
            value = e()
            if stack_frame.exit_flag:
                break
        
        return value
            
    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, repr(self.__exprs))
