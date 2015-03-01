from collections import defaultdict

METACLASSES = {}

def register_builtin_metaclass(klass, *init_params):
	name = klass.__name__
	instance = klass.__new__(klass)
	METACLASSES[name] = instance
	instance.__init__(*init_params)
	
def register_user_metaclass(instance):
	METACLASSES[instance.name] = instance
	
def get_metaclass(name):
	return METACLASSES[name]

class Root:
	def __init__(self, metaclass, superclass=None):
		self.__metaclass = metaclass
		self.__superclass = superclass
		
	def call_method(self, name, *params):
		method_to_call = self.metaclass.get_method(name)
		if not method_to_call:
			if not self.super:
				raise UnsupportedMethodError(name)
			else:
				return super.call_method(name, *params)
		return method_to_call.call(self, *params)
		
	@property
	def id(self):
		return id(self)
		
	def to_string(self):
		return self.metaclass.name
		
	@property
	def metaclass(self):
		return self.__metaclass
		
	@property
	def super(self):
		return self.__superclass
		
class RootMetaclass(Root):
	def __init__(self, metaclass_name, class_name):
		metaclass = get_metaclass(metaclass_name)
		super().__init__(metaclass)
		self.__methods = defaultdict(lambda: None)
		self.__class_name = class_name
		self.add_method(ClassMethod)
		self.add_method(IdMethod)
		self.add_method(ToStringMethod)
	
	@property
	def name(self):
		return self.__class_name
		
	def add_method(self, method):
		method = method()
		self.__methods[method.name] = method
		
	def has_method(self, method_name):
		return (method_name in self.__methods.keys)
	
	def get_method(self, name):
		return self.__methods[name]

class ClassMetaclass(RootMetaclass):
	def __init__(self):
		super().__init__(self.__class__.__name__, 'Metaclass')
		self.add_method(HasMethodMethod)
		self.add_method(NameMethod)

class CallableMetaclass(ClassMetaclass):
	def __init__(self, class_name):
		super().__init__(super().__class__.__name__, class_name)
		#self.add_method(CallMethod)
		
class ClosureMetaclass(CallableMetaclass):
	def __init__(self):
		super().__init__('Closure')
		#self.add_method(CallMethod)
		
class FunctionMetaclass(CallableMetaclass):
	def __init__(self):
		super().__init__('Function')
		#self.add_method(CallMethod)
		
class MethodMetaclass(CallableMetaclass):
	def __init__(self):
		super().__init__('Method')
		#self.add_method(CallMethod)

class ObjectMetaclass(RootMetaclass):
	def __init__(self, class_name):
		super().__init__('ClassMetaclass', class_name)
		self.add_method(NewMethod)

class CactiSyntaxError(Exception): pass

class UnsupportedMethodError(Exception): pass

class Statement: pass

class AssignmentExpression(Statement):
	def __init__(self):
		pass
	
	def evaluate(self, context):
		pass
		
class ValueExpression(Statement):
	def __init__(self):
		pass
		
	def evaluate(self, context):
		pass

class Block:
	def __init__(self, statements):
		self.__statements = statements
		
	def evaluate(self, context={}):
		pass

class Callable(Root):
	def __init__(self, metaclass_name, name=None, *param_names):
		super().__init__(metaclass_name)
		self.__name = name
		self.__param_names = param_names
		
	def call(self, caller, *params):
		self.check_arity(caller, *params)
		
	def check_arity(self, caller, *called_params):
		if self.arity != len(called_params):
			kwargs = {'caller': caller.metaclass.name, 'method_name': self.__name, 'exp': self.arity, 'got': len(called_params)}
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

"""
class Closure(Callable):
	def __init__(self, param_names, block, context):
		super().__init__()
		self.__param_names = param_names
		self.__block = block
		self.__external_context = self.__get_external_ref_context(context)
		
	def __get_external_ref_context(self):
		pass
		
	def call(self):
		return self.__block.evaluate(self.__external_context)
		
class Function(Callable):
	def __init__(self, function_name, param_names, block):
		super().__init__(function_name)
		self.__param_names = param_names
		self.__block = block
		
	def call(self, params):
		context = dict(zip(self.__param_names, params))
		self.__block.evaluate(context)

class Method(Callable):
	def __init__(self, method_name, param_names, block):
		super().__init__(method_name)
		self.__param_names = param_names
		self.__block = block
		
	def call(self, caller, params):
		context = dict(zip(self.__param_names, params))
		context['self'] = caller
		self.__block.evaluate(context)
"""
		
class PyMethod(Callable):
	def __init__(self, method_name, function=None, *param_names):
		super().__init__('MethodMetaclass', method_name, *param_names)
		self.__function = function
		
	def call(self, caller, *params):
		super().call(caller, *params)
		if self.__function:
			return self.__function(caller, *params)

"""
class PyBinaryOpMethod(PyMethod):
	def __init__(self, name):
		super().__init__(name)
		lookup = {'+': lambda a, b: a+b, '-': lambda a, b: a-b, '*': lambda a, b: a*b, '/': lambda a, b: a/b}
		self.__op_method = lookup[name]
		
	def call(self, caller, *params):
		self.check_arity(2, [caller] + list(params))
		return self.__op_method(caller.raw_value, params[0].raw_value)
"""
class ClassMethod(PyMethod):
	def __init__(self):
		super().__init__('class', lambda caller: caller.metaclass)

class IdMethod(PyMethod):
	def __init__(self):
		super().__init__('id', lambda caller: caller.id)
		
class NameMethod(PyMethod):
	def __init__(self):
		super().__init__('name', lambda caller: caller.name)
		
class NewMethod(PyMethod):
	def __init__(self):
		super().__init__('new', lambda caller, *params: caller.get_instance(*params))
		
class ToStringMethod(PyMethod):
	def __init__(self):
		super().__init__('to_string', lambda caller: caller.to_string())

class HasMethodMethod(PyMethod):
	def __init__(self):
		function = lambda caller, *params: caller.has_method(*params)
		param_names = ['method_name']
		super().__init__('has_method', function, param_names)

#########################################################################################

class FooToStringMethod(PyMethod):
	def __init__(self):
		super().__init__('to_string', lambda caller: 'My Foo!')
		
class RandomMethod(PyMethod):
	def __init__(self):
		import random
		super().__init__('random', lambda caller: random.random())

class Object(Root):
	def __init__(self, meta_class):
		super().__init__(meta_class)
		

register_builtin_metaclass(ClassMetaclass)

print(METACLASSES)
		
foo_metaclass = ObjectMetaclass('Foo')
foo_metaclass.add_method(FooToStringMethod)
foo_metaclass.add_method(RandomMethod)
foo_instance = Object(foo_metaclass)
print(foo_instance.call_method('to_string'))
print(foo_instance.call_method('random'))
print(foo_instance.call_method('id_foo'))
#print(foo_instance.call_method('class').call_method('has_method', *['to_string','a']))
#print(foo_instance.metaclass.name)
#print(foo_instance.id)


"""
class Object(Base):
	def __init__(self, metaclass):
		super().__init__()
		print(self.__metaclass)
		self.__metaclass = metaclass('Foo') #(self.__class__.__name__)
		

class NumberMetaclass(Metaclass):
	def __init__(self, class_name=None):
		super().__init__()
		self.add_method(PyBinaryOpMethod('+'))
		self.add_method(PyBinaryOpMethod('-'))
		self.add_method(PyBinaryOpMethod('*'))
		self.add_method(PyBinaryOpMethod('/'))
		
class Number(Object):
	def __init__(self, raw_value):
		super().__init__(NumberMetaclass)
		self.__raw_value = raw_value
		
	@property
	def raw_value(self):
		return self.__raw_value
		
class Integer(Number):
	def __init__(self, raw_value):
		super().__init__(int(raw_value))
	
class Float(Number):
	def __init__(self, raw_value):
		super().__init__(float(raw_value))

integer = Integer(5)
integer2 = Integer('100')
double1 = Float('1.56789')
print(integer.call_method('+', integer2))
print(integer.call_method('+', double1))
print(integer.call_method('class'))
meta = integer.call_method('class')
print(meta.call_method('name'))
#print(__PyMethod('+', __PyAdd))
""" 