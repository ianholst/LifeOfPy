import random
from Vector import *
from Creature import *

class Herd(object):
# Manages groups of creatures
# Like BOIDS
# TODO: make some things class attributes

	def __init__(self):
		# Initialize main data structure
		self.creatures = []
		# Herd attributes to be constantly updated
		self.center = Vector(0,0,0)
		self.averageVelocity = Vector(0,0,0)

	def add(self, creature):
		self.creatures.append(creature)

	def flock(self, dt):
		self.center = self.getCenter()
		self.averageVelocity = self.getAverageVelocity()
		for creature in self.creatures:
			creature.vel += self.seekCenter(creature)
			creature.vel += self.herdSeparation(creature)
			creature.vel += self.matchVelocity(creature)
			creature.vel += Vector(10*random.uniform(-1,1), 10*random.uniform(-1,1),0)*dt
			self.limitVelocity(creature)
			creature.move(dt)

	def seekCenter(self, creature):
		# Tendency towards the center of mass of the herd.
		vc = (self.center - creature.pos) * creature.genes["centerSeekingFactor"]
		return vc

	def herdSeparation(self, creature):
		# Prevent collisions with other creatures.
		# TODO: Main source of inefficiency, fix this
		vs = Vector(0,0,0)
		for otherCreature in self.creatures:
			if otherCreature != creature:
				if mag(creature.pos - otherCreature.pos) < creature.genes["herdingDistace"]:
					vs -= (otherCreature.pos - creature.pos)
		vs *= creature.genes["herdingSeparationFactor"]
		return vs

	def matchVelocity(self, creature):
		# Creatures try to match velocity with near creatures
		vp = (self.averageVelocity - creature.vel) * creature.genes["velocityMatchingFactor"]
		return vp

	def moveTowards(self, creature, targetPos):
		# Can be activated to steer creatures towards a certain place
		vt = (targetPos - creature.pos) * self.moveTowardsFactor
		return vt

	def getCenter(self):
		# TODO: make this faster
		center = Vector(0,0,0)
		for creature in self.creatures:
			center += creature.pos
		center /= len(self.creatures)
		return center

	def getAverageVelocity(self):
		# TODO: make this faster
		averageVelocity = Vector(0,0,0)
		for creature in self.creatures:
			averageVelocity += creature.vel
		averageVelocity /= len(self.creatures)
		return averageVelocity

	def limitVelocity(self, creature):
		# TODO: maybe make this faster too
		if mag(creature.vel) > creature.genes["velocityLimit"]:
			creature.vel = creature.genes["velocityLimit"] * unit(creature.vel)


if __name__ == '__main__':
	from Main import main
	main()