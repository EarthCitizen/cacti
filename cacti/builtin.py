from collections import defaultdict

TYPE_DEFINITIONS = defaultdict(lambda: None)

def register_type_definition(type_def, name):
    TYPE_DEFINITIONS[name] = type_def

def get_type_definition(name):
    return TYPE_DEFINITIONS[name]

class UnsupportedMethodError(Exception): pass

def get_object():
    return Object(get_type_definition('Object'), None)

# All Object Instances Have This
class Object:
    def __init__(self, type_def, superclass):
        self.__type_def = type_def
        self.__superclass = superclass
        
    def call_method(self, name, *params):
        object_searched = self
        method_to_call = None
        
        while not method_to_call:
            method_to_call = object_searched.type.get_method(name)
            if not method_to_call:
                if not object_searched.super:
                    raise UnsupportedMethodError(name)
                else:
                    object_searched = object_searched.super
        
        return method_to_call.call(self, *params)
    
        
    @property
    def id(self):
        return id(self)
        
    def to_string(self):
        return "<{}>".format(self.type.name)
        
    @property
    def type(self):
        return self.__type_def
        
    @property
    def super(self):
        return self.__superclass
    
    #def __str__(self):
    #    return self.to_string()
    
class TypeDefinition(Object):
    def __init__(self, type_name):
        # If type_name is TypeDefinition
        # then type property will be a
        # circular reference
        class_name = self.__class__.__name__
        if type_name == class_name:
            type_def = self
        else:
            type_def = get_type_definition(class_name)
        
        super().__init__(type_def, get_object())
        self.__methods = defaultdict(lambda: None)
        self.__type_name = type_name
        self.__final = False
        
    @property
    def final(self):
        return self.__final
    
    @final.setter
    def final(self, value):
        self.__final = value
    
    @property
    def name(self):
        return self.__type_name
        
    def add_method(self, method):
        self.__methods[method.name] = method
        
    def has_method(self, method_name):
        return (method_name in self.__methods.keys)
    
    def get_method(self, name):
        return self.__methods[name]
    
    def to_string(self):
        return "<{} '{}'>".format(self.__class__.__name__, self.name)
    
    
class InheritingTypeDefintition(TypeDefinition):
    def __init__(self, type_name, parent_type_def):
        super().__init__(type_name)
        self.__parent_type_def = parent_type_def
        
class Trait(TypeDefinition):
    def __init__(self, trait_name, *traits):
        super().__init__(trait_name)
        self.__traits = traits        
    
class Class(TypeDefinition):
    def __init__(self, class_name, base_class, *traits):
        super().__init__(class_name)
        self.__traits = traits
        self.__base_class = base_class
        
    def new(self):
        parent_instance = None
        if self.__base_class:
            parent_instance = self.__base_class.new()
        return Object(self, parent_instance)

    
class Callable(Object):
    def __init__(self, type_def, name, *param_names):
        super().__init__(type_def, get_object())
        self.__name = name
        self.__param_names = param_names
        
    def call(self, caller, *params):
        self.check_arity(caller, *params)
        
    def check_arity(self, caller, *called_params):
        if self.arity != len(called_params):
            kwargs = {'caller': caller.type.name, 'method_name': self.__name, 'exp': self.arity, 'got': len(called_params)}
            raise SyntaxError("{caller}.{method_name}: Expected {exp} parameter(s) but received {got}".format(**kwargs))
    
    @property
    def param_names(self):
        return self.__param_names
    
    @property
    def arity(self):
        return len(self.__param_names)
        
    @property
    def name(self):
        return self.__name
    
    def to_string(self):
        return "<{} '{}'>".format(self.type.name, self.name)
    
class Method(Callable): pass

class Function(Callable): pass
    
class PyMethod(Method):
    def __init__(self, method_name, function, *param_names):
        type_def = get_type_definition('Method')
        super().__init__(type_def, method_name, *param_names)
        self.__function = function
        
    def call(self, target, *params):
        super().call(target, *params)
        if self.__function:
            return self.__function(target, *params)
        
class TypeMethod(PyMethod):
    def __init__(self):
        super().__init__('type', lambda target: target.type)

class IdMethod(PyMethod):
    def __init__(self):
        super().__init__('id', lambda target: target.id)
        
class NameMethod(PyMethod):
    def __init__(self):
        super().__init__('name', lambda target: target.name)
        
class NewMethod(PyMethod):
    def __init__(self):
        super().__init__('new', lambda target, *params: target.get_instance(*params))
        
class ToStringMethod(PyMethod):
    def __init__(self):
        super().__init__('to_string', lambda target: target.to_string())
        
class SuperMethod(PyMethod):
    def __init__(self):
        super().__init__('super', lambda target: target.super)

class HasMethodMethod(PyMethod):
    def __init__(self):
        function = lambda target, *params: target.has_method(*params)
        param_names = ('method_name',)
        super().__init__('has_method', function, param_names)
        
class PyBinaryOpMethod(PyMethod):
    def __init__(self, method_name):
        lookup = {'+': lambda a, b: a+b, '-': lambda a, b: a-b, '*': lambda a, b: a*b, '/': lambda a, b: a/b}
        super().__init__(method_name, lookup[method_name], 'a', 'b')
        
    def call(self, caller, *params):
        super().call(self, *params)
        return self.__op_method(caller.raw_value, params[0].raw_value)
        
class PyFunction(Function):
    def __init__(self, function_name, function, *param_names):
        type_def = get_type_definition('Function')
        super().__init__(type_def, function_name, *param_names)
        self.__function = function
        
    def call(self, *params):
        super().call(self, *params)
        if self.__function:
            return self.__function(*params)
        
class SumFunction(PyFunction):
    def __init__(self):
        super().__init__('sum', lambda a, b, c: a + b + c, 'a', 'b', 'c')


object_type = TypeDefinition.__new__(TypeDefinition)
register_type_definition(object_type, 'Object')

type_definition = TypeDefinition.__new__(TypeDefinition)
register_type_definition(type_definition, 'TypeDefinition')

object_type.__init__('Object')
type_definition.__init__('TypeDefinition')

method = TypeDefinition('Method')
register_type_definition(method, method.name)

object_type.add_method(TypeMethod())
object_type.add_method(IdMethod())
object_type.add_method(ToStringMethod())
object_type.add_method(SuperMethod())

type_definition.add_method(TypeMethod())
type_definition.add_method(IdMethod())
type_definition.add_method(ToStringMethod())

method.add_method(NameMethod())

# FUNCTION

function = TypeDefinition('Function')
register_type_definition(function, function.name)

function.add_method(NameMethod())

# TRAIT

trait = TypeDefinition('Trait')
register_type_definition(trait, 'Trait')

trait.add_method(TypeMethod())
trait.add_method(IdMethod())
trait.add_method(ToStringMethod())

message_method = PyMethod('message', lambda target: 'The message is: ' + target.type.name)

foo_class = Class('Foo', None)
foo_class.add_method(message_method)
foo_inst = foo_class.new()

print(foo_class.to_string())
print(foo_inst.to_string())

some_class = Class('Some', foo_class)
some_inst = some_class.new()

print(some_class.to_string())
print(some_inst.to_string())
print(some_inst.call_method('message'))
print(some_inst.super.to_string())

# number = TypeDefinition('Number')
# register_type_definition(number)
# 
# number.add_method(PyBinaryOpMethod('+'))
# number.add_method(PyBinaryOpMethod('-'))
# number.add_method(PyBinaryOpMethod('*'))
# number.add_method(PyBinaryOpMethod('/'))
# 
# sum_instance = SumFunction()

#print(object_type.super.type.type.type.to_string())
#print(TYPE_DEFINITIONS)
#print(number.to_string())
#print(sum_instance.type.to_string())
#print(IdMethod().type.to_string())
#print(sum_instance.super.to_string())
#print(sum_instance.call(1,2,3))
#print(sum_instance.call_method('id'))
#print(sum_instance.super.type.to_string())
#print(number.to_string())
#print(method.type.type)
#print(method.type.name)
