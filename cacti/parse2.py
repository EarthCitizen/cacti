from pyparsing import *

ParserElement.enablePackrat()

from functools import reduce
import cacti.runtime as rntm
import cacti.lang as lang
import cacti.builtin as bltn
import cacti.ast as ast

__all__ = ['parse_file']

open_curl = Literal("{").suppress()
close_curl = Literal("}").suppress()
open_paren = Literal("(").suppress()
close_paren = Literal(")").suppress()

keyword_class = Keyword('class').suppress()
keyword_closure = Keyword('closure').suppress()
keyword_function = Keyword('function').suppress()
keyword_method = Keyword('method').suppress()
keyword_var = Keyword('var').suppress()
keyword_val = Keyword('val').suppress()

value = Forward()

identifier = Word('_' + alphas, bodyChars='_' + alphanums)
identifier.setName('ID')

reference = identifier.copy()
def reference_action(s, loc, toks):
    return ast.ReferenceExpression(toks[0])
reference.setParseAction(reference_action)

integer = Word(nums).setResultsName('value')
def integer_action(s, loc, toks):
    return ast.ValueExpression(bltn.make_integer(int(toks.value)))
integer.setParseAction(integer_action)

string = QuotedString('"', escChar='\\').setResultsName('value')
def string_action(s, loc, toks):
    return ast.ValueExpression(bltn.make_string(str(toks.value)))
string.setParseAction(string_action)

call_operator = open_paren + Group(Optional(delimitedList(value))) + close_paren
def call_operator_action(s, loc, toks):
    return reduce(lambda o1, o2: ast.OperationExpression(o1, '()', *o2), toks[0])

#property_operator = Group(OneOrMore(Literal('.').suppress() + identifier)
def property_operator_action(s, loc, toks):
    return ast.PropertyExpression(toks[0][0], *toks[0][1])

def binary_operation_action(s, loc, toks):
    operation = toks[0][1]
    operands = toks[0][0::2]
    expr = reduce(lambda o1, o2: ast.OperationExpression(o1, operation, o2), operands)
    return expr

operators = [
    ('.', 2, opAssoc.LEFT), #, property_operator_action),
    (call_operator, 1, opAssoc.LEFT, call_operator_action),
    ("*", 2, opAssoc.LEFT, binary_operation_action),
    ("/", 2, opAssoc.LEFT, binary_operation_action),
    ("+", 2, opAssoc.LEFT, binary_operation_action),
    ("-", 2, opAssoc.LEFT, binary_operation_action)
]

operand = (reference | integer | string)

value <<= (infixNotation(operand, operators))

#r = value.parseString("x.string.other.other(7.string, 5) * 7 - 12", parseAll=True)
#print(r)

#x = value.parseString('x.string', parseAll=True)
#print(x)

def parse_file(file):
    #return block.parseFile(file, parseAll=True)[0]
    return value.parseFile(file, parseAll=True)


