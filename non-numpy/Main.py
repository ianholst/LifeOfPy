import pyglet
from pyglet.gl import *
from pyglet.window import key, mouse
from Vector import *
from Creature import *
from Environment import *
from Models import *
from GUI import *
from Window import *
import math


def main():
	random.seed(0)
	environment = Environment(gridSize=32, cellSize=10, terrainResolution=128)
	window = Window(environment)
	window.start()


if __name__ == '__main__':
	main()