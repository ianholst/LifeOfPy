import pyglet
from pyglet.gl import *
import random
from Vector import Vector, mag, unit
from Creature import *

class Herd:
# Manages groups of creatures
# Like BOIDS

	def __init__(self):
		# Initialize main data structure
		self.creatureList = []
		self.selectedCreature = None
		# Eventually these will be specified for each creature

		self.centerSeekingFactor = 1/100
		self.centerSeekingOn = 1

		self.herdingSeparation = 30
		self.herdingSeparationFactor = 1
		self.herdingSeparationOn = 1

		self.velocityMatchingFactor = 1/6
		self.velocityMatchingOn = 1

		self.velocityLimit = 25
		self.boundaryCorrectionSpeed = 10

		self.center = Vector(0,0)
		self.averageVelocity = Vector(0,0)


	def add(self, creature):
		self.creatureList.append(creature)

	def flock(self, dt):
		self.center = self.getCenter()
		self.averageVelocity = self.getAverageVelocity()
		for creature in self.creatureList:
			v1 = self.seekCenter(creature) * self.centerSeekingOn
			v2 = self.herdSeparation(creature) * self.herdingSeparationOn
			v3 = self.matchVelocity(creature) * self.velocityMatchingOn
			self.boundPosition(creature)
			creature.vel += (v1 + v2 + v3)
			creature.vel += Vector(1000*random.uniform(-1,1), 1000*random.uniform(-1,1))*dt
			self.limitVelocity(creature)
			creature.move(dt)

	def seekCenter(self, creature):
		# Tendency towards the center of mass of the herd.
		vc = (self.center - creature.pos) * self.centerSeekingFactor
		return vc

	def herdSeparation(self, creature):
		# Prevent collisions with other creatures.
		# TODO: Main source of inefficiency, fix this
		vs = Vector(0,0)
		for otherCreature in self.creatureList:
			if otherCreature != creature:
				if mag(creature.pos - otherCreature.pos) < self.herdingSeparation:
					vs -= (otherCreature.pos - creature.pos)
		vs *= self.herdingSeparationFactor
		return vs

	def matchVelocity(self, creature):
		# Creatures try to match velocity with near creatures
		vp = (self.averageVelocity - creature.vel) * self.velocityMatchingFactor
		return vp

	def boundPosition(self, creature):
		v = Vector(0,0)
		xmin = 0
		xmax = window.width
		ymin = 0
		ymax = window.height
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
		center = Vector(0,0)
		for creature in self.creatureList:
			center += creature.pos
		center /= len(self.creatureList)
		return center

	def getAverageVelocity(self):
		averageVelocity = Vector(0,0)
		for creature in self.creatureList:
			averageVelocity += creature.vel
		averageVelocity /= len(self.creatureList)
		return averageVelocity

	def limitVelocity(self, creature):
		if mag(creature.vel) > self.velocityLimit:
			creature.vel = self.velocityLimit * unit(creature.vel)


##################### RUN #####################

config = Config(sample_buffers=1, samples=2)

window = pyglet.window.Window(width=1500, height=1000, caption="Herding Demo", 
	resizable=True, vsync=False, config=config, fullscreen=False)

# Panning and zooming
viewLeft = 0
viewRight = window.width
viewBottom = 0
viewTop = window.height
zoomLevel = 1
zoomedWidth  = window.width
zoomedHeight = window.height
zoomFactor = 1.2
maxZoomIn = 0.1
maxZoomOut = 10

@window.event
def on_resize(width, height):
	# Set window values
	global viewLeft, viewRight, viewBottom, viewTop, zoomLevel, zoomedWidth, zoomedHeight, zoomInFactor, zoomOutFactor, maxZoomIn, maxZoomOut
	viewLeft   = 0
	viewRight  = width
	viewBottom = 0
	viewTop    = height

@window.event
def on_mouse_press(x, y, button, modifiers):
	worldClick = mouseToWorld(Vector(x,y))
	for creature in herd.creatureList:
		if (creature.pos.x - creature.size <= worldClick.x <= creature.pos.x + creature.size and
			creature.pos.y - creature.size <= worldClick.y <= creature.pos.y + creature.size):
			herd.selectedCreature = creature
			break

@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
	if herd.selectedCreature != None:
		worldClick = mouseToWorld(Vector(x,y))
		herd.selectedCreature.pos = worldClick
		herd.selectedCreature.vel = Vector(0,0)
		# Throw mode
		#herd.selectedCreature.vel = 20*Vector(dx,dy)
	# Display dragging
	else:
		global viewLeft, viewRight, viewBottom, viewTop, zoomLevel, zoomedWidth, zoomedHeight, zoomInFactor, zoomOutFactor, maxZoomIn, maxZoomOut
		viewLeft   -= dx*zoomLevel
		viewRight  -= dx*zoomLevel
		viewBottom -= dy*zoomLevel
		viewTop    -= dy*zoomLevel


@window.event
def on_mouse_release(x, y, button, modifiers):
	if herd.selectedCreature != None:
		herd.selectedCreature = None


@window.event
def on_mouse_scroll(x, y, dx, dy):
	global viewLeft, viewRight, viewBottom, viewTop, zoomLevel, zoomedWidth, zoomedHeight, zoomInFactor, zoomOutFactor, maxZoomIn, maxZoomOut
	# Get scale factor
	f = zoomFactor**-dy
	# If zoomLevel is in the proper range
	if maxZoomIn < zoomLevel*f < maxZoomOut:
		zoomLevel *= f

		mouseX = x / window.width
		mouseY = y / window.height

		worldX = viewLeft + mouseX * zoomedWidth
		worldY = viewBottom + mouseY * zoomedHeight

		zoomedWidth *= f
		zoomedHeight *= f

		viewLeft   = worldX - mouseX * zoomedWidth
		viewRight  = worldX + (1 - mouseX) * zoomedWidth
		viewBottom = worldY - mouseY * zoomedHeight
		viewTop    = worldY + (1 - mouseY) * zoomedHeight

def mouseToWorld(pos):
	global viewLeft, viewRight, viewBottom, viewTop, zoomLevel, zoomedWidth, zoomedHeight, zoomInFactor, zoomOutFactor, maxZoomIn, maxZoomOut

	mouseX = pos.x / window.width
	mouseY = pos.y / window.height
	worldX = viewLeft + mouseX * zoomedWidth
	worldY = viewBottom + mouseY * zoomedHeight

	return Vector(worldX, worldY)

def drawCreatures():
	for creature in herd.creatureList:
		drawCircle(creature.pos.x, creature.pos.y, creature.size-2, creature.size)
		#drawPoint(creature.pos.x, creature.pos.y)
		pass

def drawCircle(x, y, inner, outer, color=(1,1,1,0.5)):
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
	drawCircle(creature.pos.x, creature.pos.y, creature.size-3, creature.size, color=(1,0,0,1))

def drawCenterOfMass():
	drawCircle(herd.getCenter().x, herd.getCenter().y, 0, 30, color=(0,0.5,0,1))

@window.event
def on_draw():
	window.clear()
	
	# Initialize Projection matrix
	glMatrixMode( GL_PROJECTION )
	glLoadIdentity()

	# Initialize Modelview matrix
	glMatrixMode( GL_MODELVIEW )
	glLoadIdentity()

	# Set orthographic projection matrix
	glOrtho(viewLeft, viewRight, viewBottom, viewTop, 1, -1 )

	drawCenterOfMass()
	drawCreatures()
	if herd.selectedCreature != None:
		drawSelector(herd.selectedCreature)
	fps_display.draw()

def update(dt):
	herd.flock(timeFactor*dt)


herd = Herd()
N = 100
for n in range(N):
	herd.add(Creature(age=0, energy=100, size=10, 
		pos=Vector( window.width*random.random(), window.height*random.random())))
timeFactor = 1
fps_display = pyglet.clock.ClockDisplay(format="%(fps).1f", color=(0.5, 0.5, 0.5, 0.5))
pyglet.clock.schedule(update)
pyglet.app.run()
