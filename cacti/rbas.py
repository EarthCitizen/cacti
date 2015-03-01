__name__ = "rbas"

def verify_assignment(s, l, t):
	if not isinstance(t[0][0], ValueVariable):
		raise AssignmentSyntaxException(s, l, t)

class SyntaxErrorException(Exception):
	def __init__(self, s, loc, toks):
		self.s = s
		self.loc = loc
		self.toks = toks
		self.message = "Syntax Error in: {}".format(s)
		
	def __str__(self):
		return self.message

class AssignmentSyntaxException(SyntaxErrorException):
	def __init__(self, s, loc, toks):
		super().__init__(s, loc, toks)
		self.message = "Left operand of assignment not a variable: {}".format(toks[0][0])

class ValueInteger:
	def __init__(self, s, l, t):
		self.__value = int(t[0])
		
	def __str__(self):
		return str(self.__value)
		
	def __repr__(self):
		return str(self)
		
	def value(self):
		return self.__value

#def process_integer(s, l, t):
#	return ValueInteger(t[0])
	
class ValueVariable:
	def __init__(self, s, l, t):
		self.__name = t[0]
		
	def __str__(self):
		return self.__name
		
	def __repr__(self):
		return str(self)
		
#def process_value_variable(s, l, t):
#	return ValueVariable(t[0])

class ValueFunctionCall:
	def __init__(self, s, l, t):
		self.__name = t[0]
		self.__params = t[1]
		
	def __as_text(self, param_converter):
		#print([s.__class__ for s in self.__params])
		return "{0}({1})".format(self.__name, ", ".join([param_converter(i) for i in self.__params]))
	
	def __str__(self):
		return self.__as_text(str)
		
	def __repr__(self):
		return str(self)

class Expression:
	pass
	
class ExpressionTwoOperand(Expression):
	def __init__(self, s, l, t):
		self.__lho = t[0][0]
		self.__opr = t[0][1]
		self.__rho = t[0][2]
		
	@property
	def lho(self):
		return self.__lho
		
	@property
	def rho(self):
		return self.__rho
		
	def __str__(self):
		return "({} {} {})".format(str(self.__lho), self.__opr, str(self.__rho))
		
	def __repr__(self):
		return str(self)
	
class ExpressionAdd(ExpressionTwoOperand):
	def value(self):
		return self.lho.value() + self.rho.value()


		
#def process_function_call(s, l, t):
#	return ValueFunctionCall(t[0],t[1])
	
class ValueVariableAssignment:
	def __init__(self, s, l, t):
		self.__name = t[0]
		self.__value = t[1]
		
	def __as_text(self, param_converter):
		return "{0} = {1}".format(self.__name, param_converter(self.__value))
	
	def __str__(self):
		return self.__as_text(str)
		
	def __repr__(self):
		return self.__as_text(repr)
		
#def process_value_variable_assignment(s, l, t):
#	return ValueVariableAssignment(t[0], t[1])

"""
def process_exp_value(s, l, t):
	return ValueExpression(t[0])

def process_variable_reference(s, l, t):
	return VariableReference(t[0])
	
def process_numeric_value(s, l, t):
	return NumericValue(t[0])
	
def process_stm_print(s, l, t):
	return StatementPrint(t.value)

def process_stm_var_dec(s, l, t):
	return StatementVarDeclaration(t.var_ref, t.value)
	
class ValueExpression:
	def __init__(self, value_holder):
		self.__value_holder = value_holder
		
	def value(self, env):
		return self.__value_holder.value(env)

class VariableReference:
	def __init__(self, var_name):
		self.name = var_name
		
	def value(self, env):
		return env.get_var(self.name)
		
class NumericValue:
	def __init__(self, value):
		self.__value = value
		
	def value(self, env):
		return self.__value
	
class Environment:
	def __init__(self):
		self.__vars = {}
	
	def get_var(self, var_name):
		return self.__vars
	
	def set_var(self, var_name, value):
		self.__vars[var_name] = value

class Program:
	def __init__(self, statements):
		self.__statements = statements
		
	def statements(self):
		return self.__statements
		
	def execute(self):
		env = Environment()
		for stmt in self.__statements:
			stmt.run(env)

class StatementPrint:
	def __init__(self, value):
		self.__value = value
		
	def run(self, env):
		print(self.__value.value(env))

class StatementVarDeclaration:
	def __init__(self, var_ref, value):
		self.__var_name = var_ref.name
		self.__value = value
		
	def run(self, env):
		pass #env.set_var(self.__var_name, self.__value.value(env))
"""
		