from cacti.lang import SymbolTable

GLOBAL_SYMBOLS = SymbolTable()

cls = GLOBAL_SYMBOLS['Foo']

params = []

obj = cls.get_hook('new').call(*params)

obj.get_hook('+').call(123)
obj.get_property('something')
obj.get_property('some_method').call()




class PropertyDefinition:
    pass


class Method:
    pass

m = Method(bind)

class ValDefinition:
    pass

class VarDefinition:
    pass

class MethodDefinition:
    pass

class ClassDefinition:
    pass


