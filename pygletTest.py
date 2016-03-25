import pyglet
from pyglet.gl import *
from Creature import Creature
import random
from Vector import Vector, mag, unit

class Herd:
# Manages groups of creatures

	def __init__(self, N):
		self.N = N
		self.creatureList = [Creature(age=0, energy=100, size=10, 
			pos=Vector(1000*random.random(),1000*random.random())) for x in range(N)]
		self.k = -100
		self.selectedCreature = None
		self.herdingDistance = 500
		self.herdRadius = 100

	def calculateForces(self):
		#center = self.getCenter()
		for creature in self.creatureList:
			creature.netForce = Vector(0,0)
			#centerRadius = creature.pos - center
			#if mag(centerRadius) > self.herdRadius:
				#creature.netForce += self.k * unit(centerRadius)
			#else:
				#creature.netForce += self.k * creature.vel
			for otherCreature in creature.closeParticles:
				r = mag(creature.pos - otherCreature.pos)
				rhat = unit(creature.pos - otherCreature.pos)
				creature.netForce += self.k / r * rhat

	def getCloseParticles(self):
		for creature in self.creatureList:
			creature.closeParticles = []
			for otherCreature in self.creatureList:
				if otherCreature != creature:
					if mag(creature.pos - otherCreature.pos) < self.herdingDistance:
						creature.closeParticles += [otherCreature]

	def move(self, dt):
		self.getCloseParticles()
		self.calculateForces()
		for creature in self.creatureList:
			creature.takeStep(dt)

	def getCenter(self):
		center = Vector(0,0)
		for creature in self.creatureList:
			center += creature.pos
		center /= len(self.creatureList)
		return center

window = pyglet.window.Window(width=1000, height=1000, caption="Term Project Demo", resizable=True)

@window.event
def on_mouse_press(x, y, button, modifiers):
	for creature in herd.creatureList:
		if (creature.pos.x - creature.size <= x <= creature.pos.x + creature.size and
			creature.pos.y - creature.size <= y <= creature.pos.y + creature.size):
			herd.selectedCreature = creature
			break

@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
	if herd.selectedCreature != None:
		herd.selectedCreature.pos = Vector(x, y)
		herd.selectedCreature.vel = Vector(0,0)
		# Throw mode
		#herd.selectedCreature.vel = 20*Vector(dx,dy)

@window.event
def on_mouse_release(x, y, button, modifiers):
	if herd.selectedCreature != None:
		herd.selectedCreature = None


@window.event
def on_mouse_scroll(x, y, dx, dy):
	pass

def drawCreatures():
	for creature in herd.creatureList:
		#pyglet.graphics.draw(1, GL_POINTS, ('v2f',(creature.pos.x,creature.pos.y)))
		draw_circle(creature.pos.x, creature.pos.y, creature.size-2, creature.size)

def draw_circle(x, y, inner, outer, color=(1,1,1,1)):
	'''draws a ring of inner radius "inner" and outer radius "outer"
	   centered at (x, y).'''
	glPushMatrix()
	glColor4f(*color)
	glTranslatef(x, y, 0)
	q = gluNewQuadric()
	# a circle is written as a number of triangular slices; we use
	# a maximum of 360 which looked smooth even for a circle as
	# large as 1500 px.
	# Smaller circles can be drawn with fewer slices - the rule we
	# use amount to approximately 1 slice per px on the circumference
	slices = min(360, 6*outer)
	gluDisk(q, inner, outer, slices, 1)
	glPopMatrix()

def drawSelector(creature):
	draw_circle(creature.pos.x, creature.pos.y, creature.size-3, creature.size, color=(1,0,0,0))

@window.event
def on_draw():
	window.clear()
	drawCreatures()
	if herd.selectedCreature != None:
		drawSelector(herd.selectedCreature)
	fps_display.draw()

timeFactor = 1
def update(dt):
	herd.move(timeFactor*dt)

herd = Herd(50)
fps_display = pyglet.clock.ClockDisplay(format="%(fps).1f", color=(0.5, 0.5, 0.5, 1))
pyglet.clock.schedule_interval(update, 1/100)
pyglet.app.run()