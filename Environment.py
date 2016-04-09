import pyglet
from pyglet.gl import *
from pyglet.window import key, mouse
from Vector import *
from Creature import *
from Herd import *

class Environment:
# Should handle all interactions between creatures, herds, and environmental objects
# Assuming almost no user interaction?

	def __init__(self):
		self.herds = []
		self.selectedCreature = None
		# Random environment elements

	def createHerd(self, N):
		herd = Herd()
		for n in range(N):
			herd.add(Creature(age=0, energy=100, size=10, 
				pos=Vector(1000*random.random(), 1000*random.random(), 0)))
				# Position will be decided by the user
		self.herds.append(herd)

	def update(self, dt):
		for herd in self.herds:
			herd.flock(dt)