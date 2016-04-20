import pyglet
from pyglet.gl import *
from pyglet.window import key, mouse
from Vector import *
from Creature import *
from Herd import *
from Environment import *
from Models import *
from GUI import *
import math
from Window import *

#create herd
	#inside herd make creatures

def main():
	random.seed(90)
	environment = Environment(50, 100)
	window = Window(environment)
	window.start()



if __name__ == '__main__':
	main()