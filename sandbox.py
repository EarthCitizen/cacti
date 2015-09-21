class Foo:
	def __init__(self, *values=None):
		self.__values = values

	def get_values(self):
		return self.__values

a = [1,2,3]

f = Foo(values=*a)

print(f.get_values())
