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

		self.centerSeekingFactor = 1/100
		self.centerSeekingOn = True

		self.herdingSeparation = 40
		self.herdingSeparationFactor = 1
		self.herdingSeparationOn = True

		self.velocityMatchingFactor = 1/100
		self.velocityMatchingOn = True

		self.moveTowardsFactor = 1/100
		self.moveTowardsPos = Vector(100,100,0)

		self.velocityLimit = 25
		self.boundaryCorrectionSpeed = 10

		self.center = Vector(0,0,0)
		self.averageVelocity = Vector(0,0,0)


	def add(self, creature):
		self.creatures.append(creature)

	def flock(self, dt):
		self.center = self.getCenter()
		self.averageVelocity = self.getAverageVelocity()
		for creature in self.creatures:
			if self.centerSeekingOn:
				v1 = self.seekCenter(creature)
			else: v1 = Vector(0,0,0)
			if self.herdingSeparationOn:
				v2 = self.herdSeparation(creature)
			else: v2 = Vector(0,0,0)
			if self.velocityMatchingOn:
				v3 = self.matchVelocity(creature)
			else: v3 = Vector(0,0,0)
			#v4 = self.moveTowards(creature, self.moveTowardsPos)
			#self.boundPosition(creature)
			creature.vel += (v1 + v2 + v3)# + v4)
			#creature.vel += Vector(100*random.uniform(-1,1), 100*random.uniform(-1,1))*dt
			self.limitVelocity(creature)
			creature.move(dt)

	def seekCenter(self, creature):
		# Tendency towards the center of mass of the herd.
		vc = (self.center - creature.pos) * self.centerSeekingFactor
		return vc

	def herdSeparation(self, creature):
		# Prevent collisions with other creatures.
		# TODO: Main source of inefficiency, fix this
		vs = Vector(0,0,0)
		for otherCreature in self.creatures:
			if otherCreature != creature:
				if mag(creature.pos - otherCreature.pos) < self.herdingSeparation:
					vs -= (otherCreature.pos - creature.pos)
		vs *= self.herdingSeparationFactor
		return vs

	def matchVelocity(self, creature):
		# Creatures try to match velocity with near creatures
		vp = (self.averageVelocity - creature.vel) * self.velocityMatchingFactor
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
		if mag(creature.vel) > self.velocityLimit:
			creature.vel = self.velocityLimit * unit(creature.vel)