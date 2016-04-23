import random
from Vector import *


class Creature(object):

	def __init__(self, age, energy, size, pos, vel=Vector(0,0,0)):
		self.age = age
		self.energy = energy
		self.size = size
		self.pos = pos
		self.vel = vel
		self.body = [{"type":"core", "color":(.4,.3,0), "radius":1}, 
						[{"type":"limb", "color":(.4,.3,5), "length":3, "thickness":0.3, "angle":0}],
						[{"type":"limb", "color":(.4,.3,0), "length":3, "thickness":0.3, "angle":-225},
							[{"type":"limb", "color":(.4,.3,0), "length":5, "thickness":0.3}],
							[{"type":"limb", "color":(.4,.3,0), "length":5, "thickness":0.3},
								[{"type":"limb", "color":(.4,.3,0), "length":5, "thickness":0.3, "angle":0}],
								[{"type":"limb", "color":(.4,.3,0), "length":2, "thickness":0.3, "angle":0}]]]]


		self.genes = {"centerSeekingFactor":1/100,
					  "herdingSeparationFactor":1,
					  "herdingDistace":10,
					  "velocityMatchingFactor":1/100,
					  "velocityLimit":10,
					  "moveTowardsFactor":1}

	def move(self, dt):
		self.pos += self.vel * dt


if __name__ == '__main__':
	from Main import main
	main()