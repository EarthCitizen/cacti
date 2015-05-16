from pyparsing import *
import cacti.runtime as rntm
import cacti.builtin as bltn
import cacti.expression as expr

keyword_var = Keyword('var')

ident_word = lambda: Word('_' + alphas, bodyChars='_' + alphanums)

open_paren = Suppress(Literal("("))
close_paren = Suppress(Literal(")"))
assignment_operator = Suppress(Literal("="))
statement_end = Suppress(Literal(";") ^ LineEnd() ^ StringEnd())

value_expression = Forward()

ident = ident_word()

integer = Word(nums)
def integer_action(s, loc, toks):
    return expr.ValueExpression(bltn.make_integer(int(toks[0])))
integer.setParseAction(integer_action)

assignment_statement = keyword_var + ident + assignment_operator + integer + statement_end

result = assignment_statement.parseString('var x = 123')

#result = ident.parseString('x', parseAll=True)

print(result)

value_reference = ident_word()
def value_reference_action(s, loc, toks):
    return expr.ReferenceExpression(toks[0])
value_reference.setParseAction(value_reference_action)

add_things = value_reference + Literal('+') + integer
def add_things_action(s, loc, toks):
    return expr.OperationExpression(toks[0], toks[1], toks[2])
add_things.setParseAction(add_things_action)


call_env = rntm.CallEnv(bltn.make_object(), 'main')
table = rntm.SymbolTable()
table.add_symbol('x', rntm.ConstantValueHolder(bltn.make_integer(100)))
call_env.symbol_stack.push(table)
rntm.push_call_env(call_env)
result = add_things.parseString('x + 45')
print(result)
print(result[0]())
