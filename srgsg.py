from __future__ import division
from pyglet import window 
from pyglet.gl import * 
from pyglet.gl.glu import * 
import pyglet.clock 
from pyglet.window import key, mouse

def resize(width, height): 
	if height==0: 
		height=1 
	glViewport(0, 0, width, height) 
	glMatrixMode(GL_PROJECTION) 
	glLoadIdentity() 
	gluPerspective(90, width/height, 0.1, 1000.0) 
	glMatrixMode(GL_MODELVIEW) 
	glLoadIdentity() 

def init(): 
	glShadeModel(GL_SMOOTH) 
	glClearColor(0.0, 0.0, 0.0, 0.0) 
	glClearDepth(1.0) 
	glEnable(GL_DEPTH_TEST) 
	glDepthFunc(GL_LEQUAL) 
	glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST) 
	glEnable(GL_LIGHTING)
	glEnable(GL_LIGHT0)
	glEnable(GL_LIGHT1)

	# Define a simple function to create ctypes arrays of floats:
	def vec(*args):
		return (GLfloat * len(args))(*args)

	glLightfv(GL_LIGHT0, GL_DIFFUSE, vec(1, 1, 1, 1))
	glLightfv(GL_LIGHT1, GL_POSITION, vec(1, 0, .5, 0))
	glLightfv(GL_LIGHT1, GL_DIFFUSE, vec(.5, .5, .5, 1))
	glLightfv(GL_LIGHT1, GL_SPECULAR, vec(1, 1, 1, 1))

	glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, vec(0.5, 0, 0.3, 1))
	glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 50)

d = -40
r = 0

def draw(): 
	glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT) 
	glLoadIdentity()
	glTranslatef(0, 0, d)

	sphere = gluNewQuadric()
	gluSphere(sphere,15,30,30)


win = window.Window(width=1400,height=1000,visible=False)
win.on_resize=resize


@win.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
	if buttons & mouse.MIDDLE:
		global d
		d += dy
		glTranslatef(0, 0, d)
	if buttons & mouse.LEFT:
		global r
		r += dx
		glMatrixMode(GL_MODELVIEW)
		glRotatef(r, 0, 1, 0)

init()
win.set_visible()
clock=pyglet.clock.Clock()

while not win.has_exit:
	win.dispatch_events()
	draw()
	win.flip()
	clock.tick()

print("fps: %d" % clock.get_fps() )