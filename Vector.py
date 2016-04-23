# 3D vector class with basic operations
# Offers dot product, cross product, 
# Uses real division (import from future in Python 2)

from __future__ import division

class Vector(object):

	def __init__(self, x, y, z):
		self.x = x
		self.y = y
		self.z = z

	# Arithmetic operations
	def __add__(self, other):
		if type(other) == Vector:
			return Vector(self.x + other.x, self.y + other.y, self.z + other.z)
		else:
			raise TypeError("Can only add vectors to vectors")

	def __sub__(self, other):
		if type(other) == Vector:
			return Vector(self.x - other.x, self.y - other.y, self.z - other.z)
		else:
			raise TypeError("Can only subtract vectors with vectors")

	def __mul__(self, other):
		if type(other) == int or type(other) == float:
			return Vector(self.x * other, self.y * other, self.z * other)
		else:
			raise TypeError("Can only multiply vectors with scalars")

	def __div__(self, other):
		return self.__truediv__(other)

	def __truediv__(self, other):
		if type(other) == int or type(other) == float:
			return Vector(self.x / other, self.y / other, self.z / other)
		else:
			raise TypeError("Can only divide vectors by scalars")

	def __radd__(self, other):
		return self.__add__(other)

	def __rsub__(self, other):
		return other.__sub__(self)

	def __rmul__(self, other):
		return self.__mul__(other)

	def __rdiv__(self, other):
		return other.__rtruediv__(self)

	def __rtruediv__(self, other):
		raise TypeError("Cannot divide by a vector")

	def __pos__(self): return self
	def __neg__(self): return Vector(-self.x, -self.y, -self.z)

	# Output when printed
	def __repr__(self):
		return "<" + str(self.x) + ", " + str(self.y) + ", " + str(self.z) + ">"

	def __iter__(self):
		return iter([self.x, self.y, self.z])


# Vector operations, called as functions

def dot(v1, v2):
	return (v1.x * v2.x + v1.y * v2.y + v1.z * v2.z)

def cross(v1, v2):
		x = v1.y * v2.z - v1.z * v2.y
		y = v1.z * v2.x - v1.x * v2.z
		z = v1.x * v2.y - v1.y * v2.x
		return Vector(x, y, z)

def unit(v):
	if mag(v) != 0:
		return Vector(v.x / mag(v), v.y / mag(v), v.z / mag(v))
	else:
		return Vector(0,0,0)

def mag(v):
	return (v.x**2 + v.y**2 + v.z**2) ** (1/2)
