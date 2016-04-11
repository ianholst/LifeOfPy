import cProfile
import Vector
import Creature
import Herd
import Environment
import GUI
import Window

def profileEnvironment():
	environment = Environment.Environment()
	environment.createHerd(100)
	for n in range(100):
		environment.update(1/100)

def profileWindow():
	Window.main()

cProfile.run("profileWindow()", sort="cumtime")