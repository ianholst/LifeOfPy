import random
from Vector import Vector, mag, unit

class Creature:

	def __init__(self, age, energy, size, pos, vel=Vector(0,0)):
		self.age = age
		self.energy = energy
		self.size = size
		self.pos = pos
		self.vel = vel

	def takeStep(self, dt):
		# Randomly move in a direction
		self.vel += self.netForce * dt
		self.pos += self.vel * dt
		#self.pos += Vector(10*random.uniform(-1,1), 10*random.uniform(-1,1))

