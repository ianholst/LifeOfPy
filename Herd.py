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

		# Eventually these will be specified for each creature

		self.boundaryCorrectionSpeed = 10

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
			#v4 = self.moveTowards(creature, self.moveTowardsPos)
			#self.boundPosition(creature)
			#creature.vel += Vector(100*random.uniform(-1,1), 100*random.uniform(-1,1))*dt
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

	def boundPosition(self, creature, xmin, xmax, ymin, ymax):
		# TODO: figure out how to do this in a dynamic environment
		v = Vector(0,0,0)
		if creature.pos.x < xmin:
			v.x = self.boundaryCorrectionSpeed
		elif creature.pos.x > xmax:
			v.x = -self.boundaryCorrectionSpeed
		if creature.pos.y < ymin:
			v.y = self.boundaryCorrectionSpeed
		elif creature.pos.y > ymax:
			v.y = -self.boundaryCorrectionSpeed
		# If velocity has changed
		if v.x != 0 or v.y != 0:
			creature.vel = v

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