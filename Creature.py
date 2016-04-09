import random
from Vector import *

class Creature:

	def __init__(self, age, energy, size, pos, vel=Vector(0,0,0)):
		self.age = age
		self.energy = energy
		self.size = size
		self.pos = pos
		self.vel = vel

	def move(self, dt):
		self.pos += self.vel * dt
		# Random motion (too jittery)
		#self.pos += Vector(10*random.uniform(-1,1), 10*random.uniform(-1,1))

