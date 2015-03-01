from pyparsing import *
from rbas import *


open_paren = Suppress(Literal("("))
close_paren = Suppress(Literal(")"))

ident = Word(alphas)

value_expression = Forward()

value_integer = Word(nums)
value_integer.setParseAction(ValueInteger)

value_variable = ident
value_variable.setParseAction(ValueVariable)

value_operands = Forward()

value_function_call = ident + open_paren + Group(Optional(delimitedList(value_expression))) + close_paren
value_function_call.setParseAction(ValueFunctionCall)

value_operands <<= (value_integer ^ value_variable ^ value_function_call)

value_operators = [
	("*", 2, opAssoc.LEFT),
	("/", 2, opAssoc.LEFT),
	("+", 2, opAssoc.LEFT, ExpressionAdd),
	("-", 2, opAssoc.LEFT),
	("=", 2, opAssoc.RIGHT, verify_assignment)
]

value_expression <<= infixNotation(value_operands, value_operators)

#print(value_expression.parseString("6+3-1*\nfoo(8-5)", parseAll=True))

#print(value_expression.parseString("foo(8+6,(9)/34*10)", parseAll=True))

statement = value_expression + Suppress(Literal(";") ^ LineEnd() ^ StringEnd())

#print(statement.parseString("foo(8+6,(9)/34*10)", parseAll=True))

block = OneOrMore(Group(statement))

print(block.parseString("x=foo(8+6,(9)/34*10)", parseAll=True))

#result = block.parseString("k(1,p(x,kol (4,5,6,7,8,9,0),99999999),3); ppp     = f(9, 0)", parseAll=True)
#print(result)
