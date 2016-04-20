import random
from Vector import *


class Creature(object):

	def __init__(self, age, energy, size, pos, vel=Vector(0,0,0)):
		self.age = age
		self.energy = energy
		self.size = size
		self.pos = pos
		self.vel = vel
		self.body = [{"part":"core", "color":(1,0,0), "radius":1}, 
						[{"part":"limb", "color":(0,0,1), "length":1},
						 {"part":"limb", "color":(0,0,1), "length":2}]]
		self.genes = {}

	def move(self, dt):
		self.pos += self.vel * dt
		# Random motion (too jittery)
		#self.pos += Vector(10*random.uniform(-1,1), 10*random.uniform(-1,1))




if __name__ == '__main__':
	from Main import main
	main()