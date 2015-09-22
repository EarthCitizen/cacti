import copy
import logging
from cacti.debug import get_logger
from cacti.runtime import *
from cacti.exceptions import *

__all__ = [
    'ClassDefinition', 'Closure',
    'Function',
    'Method', 'MethodDefinition', 'Module', 'ModuleAlias',
    'ObjectDefinition',
    'PropertyDefinition',
    'TypeDefinition',
    'ValDefinition', 'VarDefinition'
]

class _Call:
    def __call__(self, *params):
        return self.call(*params)

# All ObjectDefinition Instances Have This
class ObjectDefinition:
    def __init__(self, superobj, *, typeobj=None, name=''):
        self.logger = get_logger(self)
        
        self.logger.debug("superobj={}, typeobj={}, name={}".format(str(superobj), str(typeobj), name))
        
        self.__typeobj = typeobj
        self.__name = name
        self.__selfobj = self
        self.set_superobj(superobj)
        
        self.__internal_table = SymbolTable()
        
        self.__field_table = SymbolTable()
        
        parent_hook_table = superobj.hook_table if superobj else None
        self.__hook_table = SymbolTable(parent_table=parent_hook_table, symbol_validator=isvalidhook)
        
        parent_property_table = superobj.property_table if superobj else None
        self.__property_table = SymbolTable(parent_table=parent_property_table)
        
        from cacti.builtin import make_integer
        
        self.__property_table.add_symbol('id', PropertyGetValueHolder(lambda: make_integer(id(self))))
        self.__property_table.add_symbol('type', PropertyGetValueHolder(lambda: self.typeobj))
        
        self.__public_table = self.__property_table
        self.__private_table = SymbolTableChain(self.__property_table, self.__field_table)
        
    @property
    def internal_table(self):
        return self.__internal_table
        
    def set_typeobj(self, typeobj):
        self.__typeobj = typeobj
        self.logger.debug("Set typeobj of '{}' to: '{}'".format(self, str(self.__typeobj)))
        
    def set_selfobj(self, selfobj):
        self.__selfobj = selfobj
        self.logger.debug("Set selfobj of '{}' to: '{}'".format(self, str(self.__selfobj)))
        if self.__superobj:
            self.__superobj.set_selfobj(selfobj)
        
    def set_superobj(self, superobj):
        self.__superobj = superobj
        self.logger.debug("Set superobj of '{}' to: '{}'".format(self, str(self.__superobj)))
        if self.__superobj:
            self.__superobj.set_selfobj(self.__selfobj)
    
    @property
    def field_table(self):
        return self.__field_table
    
    @property
    def public_table(self):
        return self.__public_table
        
    @property
    def private_table(self):
        return self.__private_table
        
    @property
    def hook_table(self):
        return self.__hook_table
        
    @property
    def property_table(self):
        return self.__property_table
        
    @property
    def selfobj(self):
        return self.__selfobj
    
    @property
    def superobj(self):
        self.logger.debug("Returning: '{}'".format(str(self.__superobj)))
        return self.__superobj
        
    @property
    def typeobj(self):
        return self.__typeobj
        
    @property
    def name(self):
        return self.__name
        
    def set_name(self, value):
        self.__name = value
        
    def add_hook(self, method_def):
        method = method_def.make_method(self)
        self.__hook_table.add_symbol(method.name, ConstantValueHolder(method))
    
    def add_val(self, val_name, val_value):
        self.__field_table.add_symbol(val_name, ConstantValueHolder(val_value))
    
    def add_var(self, var_name, var_value):
        self.__field_table.add_symbol(var_name, ValueHolder(var_value))
        
    def add_method(self, method_def):
        method = method_def.make_method(self)
        self.__property_table.add_symbol(method.name, ConstantValueHolder(method))
        
    def add_property(self, property_def):
        value_holder = None
        property_name = property_def.name
        get_method_def = property_def.getter_method_def
        set_method_def = property_def.setter_method_def
        
        if get_method_def is None and set_method_def is None:
            value_holder = ValueHolder()
        elif get_method_def is not None and set_method_def is not None:
            value_holder = PropertyGetSetValueHolder(
                get_method_def.make_method(self),
                set_method_def.make_method(self))
        elif get_method_def is not None and set_method_def is None:
            value_holder = PropertyGetValueHolder(get_method_def.make_method(self))
        else:
            raise Exception('TBD')
        
        self.__property_table.add_symbol(property_name, value_holder)
        
        self.logger.debug("Added property {} with value holder {}".format(repr(property_name), value_holder.__class__))
        
    def __public_or_private_table(self, petitioner):
        # Is it me asking for a property?
        if petitioner is self:
            return self.private_table
        else:
            return self.public_table
    
    def __getitem__(self, symbol_name):
        petitioner = peek_stack_frame().owner
        return self.__public_or_private_table(petitioner)[symbol_name]
    
    def __setitem__(self, symbol_name, symbol_value):
        petitioner = peek_stack_frame().owner
        self.__public_or_private_table(petitioner)[symbol_name] = symbol_value
    
    def to_native_repr(self):
        return super().__repr__()
    
    def __repr__(self):
        return self.to_native_repr()
    
    #def __str__(self):
    #    return self.to_string_multi(self)
    
    
    def to_repr(self):
        return self.to_string_multi(self.selfobj)
        
    def to_lang_string(self):
        from cacti.builtin import make_string
        return make_string(self.to_string())
    
    # This is a workaround to the fact that
    # str() will not call the __str__() that
    # is dynamically added to an object instance
    def to_string(self):
        return self.to_string_multi(self.selfobj)
    
    def to_string_multi(self, selfobj):
        if (selfobj.typeobj is None):
            ret_val = '<UNKNOWN><{}>'.format(id(selfobj))
        elif (selfobj.name is None) or ('' == selfobj.name):
            ret_val = '{}<{}>'.format(selfobj.typeobj.name, id(selfobj))
        else:
            ret_val = "{}<'{}'>".format(selfobj.typeobj.name, selfobj.name)
        
        return ret_val
    
class TypeDefinition(ObjectDefinition):
    def __init__(self, superobj, name, *, typeobj=None):
        super().__init__(superobj, typeobj=typeobj, name=name)
        
        from cacti.builtin import make_string
        self.property_table.add_symbol('name', PropertyGetValueHolder(lambda: make_string(self.name)))

class Module(TypeDefinition):
    def __init__(self, name, *, parent=None):
        self.logger = get_logger(self)

        from cacti.builtin import get_type
        type_type = get_type('Type')
        module_type = get_type('Module')
        super().__init__(type_type, name, typeobj=module_type)

        self.__parent = parent
        self.__export_table = SymbolTable()
        self.__private_table = SymbolTable()
    
    @property
    def export_table(self):
        return self.__export_table

    @property
    def private_table(self):
        return self.__private_table

    @property
    def parent(self):
        return self.__parent

    def set_parent(self, parent):
        self.__parent = parent

    def __getitem__(self, symbol_name):
        return self.export_table[symbol_name]
    
    def __setitem__(self, symbol_name, symbol_value):
        self.export_table[symbol_name] = symbol_value

class ModuleAlias(TypeDefinition):
    def __init__(self, module, *only):
        assert isinstance(module, Module)

        self.logger = get_logger(self)

        from cacti.builtin import get_type
        type_type = get_type('Type')
        module_alias_type = get_type('ModuleAlias')
        super().__init__(type_type, None, typeobj=module_alias_type)

        symbol_holders = module.export_table.symbol_holder_iter()

        if only:
            symbol_holders = filter(lambda x: x[0] in only, symbol_holders)

        for s, h in symbol_holders:
            self.public_table.add_symbol(s, h)

    def __getitem__(self, symbol_name):
        return self.public_table[symbol_name]

    def __setitem__(self, symbol_name, symbol_value):
        self.public_table[symbol_name] = symbol_value

class Closure(TypeDefinition, _Call):
    def __init__(self, stack_frame, content, *param_names):
        assert isinstance(stack_frame, StackFrame)
        
        self.logger = get_logger(self)
        
        self.__stack_frame = copy.copy(stack_frame)
        self.__content = content
        self.__param_names = param_names
        
        from cacti.builtin import get_type
        type_type = get_type('Type')
        closure_type = get_type('Closure')
        super().__init__(type_type, None, typeobj=closure_type)
        
        self.hook_table.add_symbol('()', ConstantValueHolder(self))
        
    def call(self, *params):
        push_stack_frame(self.__stack_frame)
        return_value = self.__content(*params)
        pop_stack_frame()
        return return_value
        
class Function(TypeDefinition, _Call):
    def __init__(self, name, content, *param_names):
        #assert isinstance(function_callable, Callable)
        
        self.logger = get_logger(self)
        
        self.__name = name
        self.__content = content
        self.__param_names = param_names
        
        self.__callable = Callable(self.__content, *self.__param_names)
        
        from cacti.builtin import get_type
        type_type = get_type('Type')
        function_type = get_type('Function')
        super().__init__(type_type, name, typeobj=function_type)
        
        self.hook_table.add_symbol('()', ConstantValueHolder(self))
        
    def call(self, *params):
        push_stack_frame(StackFrame(self, self.__name))
        return_value = self.__callable(*params)
        pop_stack_frame()
        return return_value
        
class Method(TypeDefinition, _Call):
    def __init__(self, owner, name, content, *param_names):
        assert isinstance(owner, ObjectDefinition)
        
        self.logger = get_logger(self)
        
        self.__owner = owner
        self.__name = name
        self.__content = content
        self.__param_names = param_names
        
        self.__callable = Callable(self.__content, *self.__param_names)
        
        self.logger.debug("Create new method: owner={} name={}".format(str(self.__owner), str(self.__name)))
        
        from cacti.builtin import get_type
        type_type = get_type('Type')
        method_type = get_type('Method')
        super().__init__(type_type, name, typeobj=method_type)
        
        # Method () does not need to be bound to self as there is
        # no actual code in which it will refer to itself.
        # Instead it is a delegate for the content of the method
        # definition which is bound to the method owner
        self.hook_table.add_symbol('()', ConstantValueHolder(self))
        
        self.logger.debug("Completed new method: owner={} name={}".format(str(self.__owner), str(self.__name)))
        
    def __eq__(self, other):
        c1 = isinstance(other, self.__class__)
        c2 = self.__owner == other.__owner
        c3 = self.__name == other.__name
        c4 = self.__content == other.__content
        c5 = self.__param_names == other.__param_names
        if c1 and c2 and c3 and c4 and c5:
            return True
            
        return False

    def call(self, *params):
        self.logger.debug('Start method call')
        stack_frame = StackFrame(self.__owner, self.__name)
        push_stack_frame(stack_frame)
        self.logger.debug('Pushed new call env')
        super_self = stack_frame.symbol_stack.peek()
        
        selfobj = self.__owner.selfobj
        superobj = self.__owner.superobj
        
        self.logger.debug('Owner: {}'.format(str(self.__owner)))
        
        self.logger.debug('Adding self: ' + str(selfobj))
        super_self.add_symbol('self', ConstantValueHolder(selfobj))
        
        self.logger.debug('Adding super: ' + str(superobj))
        super_self.add_symbol('super', ConstantValueHolder(superobj))
        
        return_value = self.__callable(*params)
        self.logger.debug('Returning: ' + str(return_value))
        
        pop_stack_frame()
        return return_value
    
class ClassDefinition(TypeDefinition):
    def __init__(self, superobj, name, *, superclass=None):
        from cacti.builtin import get_type
        typeobj = get_type('Class')
        super().__init__(superobj, typeobj=typeobj, name=name)
        self.__superclass = superclass
        self.__hook_defs = []
        self.__val_defs = []
        self.__var_defs = []
        self.__method_defs = []
        self.__property_defs = []
        
    def set_superclass(self, superclass):
        self.__superclass = superclass
        
    @property
    def superclass(self):
        return self.__superclass
        
    @property
    def hook_definitions(self):
        return self.__hook_defs
        
    @property
    def val_definitions(self):
        return self.__val_defs
        
    @property
    def var_definitions(self):
        return self.__var_defs
        
    @property
    def method_definitions(self):
        return self.__method_defs
        
    @property
    def property_definitions(self):
        return self.__property_defs
        
    def add_hook_definition(self, hook_def):
        self.__hook_defs += [hook_def]
        
    def add_val_definition(self, val_def):
        self.__val_defs += [val_def]
        
    def add_var_definition(self, var_def):
        self.__var_defs += [var_def]
        
    def add_method_definition(self, method_def):
        self.__method_defs += [method_def]
        
    def add_property_definition(self, prop_def):
        self.__property_defs += [prop_def]
        
    def __str__(self):
        return '{}<{}>'.format('Class', self.name)

class MethodDefinition:
    def __init__(self, name, content, *param_names):
        self.__name = name
        self.__content = content
        self.__param_names = param_names
        
    @property
    def name(self):
        return self.__name
        
    @property
    def content(self):
        return self.__content
        
    @property
    def param_names(self):
        return self.__param_names
        
    def make_method(self, owner):
        return Method(owner, self.name, self.content, *self.param_names)
        
class PropertyDefinition:
    def __init__(self, property_name, getter_method_def=None, setter_method_def=None):
        self.__property_name = property_name
        self.__getter_method_def = getter_method_def
        self.__setter_method_def = setter_method_def
        
    @property
    def name(self):
        return self.__property_name
        
    @property
    def getter_method_def(self):
        return self.__getter_method_def
        
    def set_getter_method_def(self, method_def):
        self.__getter_method_def = method_def
        
    @property
    def setter_method_def(self):
        return self.__setter_method_def
        
    def set_setter_method_def(self, method_def):
        self.__setter_method_def = method_def
        
class ValDefinition:
    def __init__(self, val_name, val_init_expr):
        self.__val_name = val_name
        self.__val_init_expr = val_init_expr
        
    @property
    def name(self):
        return self.__val_name
        
    @property
    def init_expr(self):
        return self.__val_init_expr
        
    def __repr__(self):
        return "{}({}, {})".format(self.__class__.__name__, repr(self.__val_name), repr(self.__val_init_expr))

class VarDefinition:
    def __init__(self, val_name, val_init_expr):
        self.__val_name = val_name
        self.__val_init_expr = val_init_expr
        
    @property
    def name(self):
        return self.__val_name
        
    @property
    def init_expr(self):
        return self.__val_init_expr
        
    def __repr__(self):
        return "{}({}, {})".format(self.__class__.__name__, repr(self.__val_name), repr(self.__val_init_expr))

