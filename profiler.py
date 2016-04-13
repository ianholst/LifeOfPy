import cProfile
import Vector
import Creature
import Herd
import Environment
import GUI
import Window

def profileEnvironment():
	environment = Environment.Environment()
	environment.createHerd(20)
	for n in range(100):
		environment.update(1/100)

def profileWindow():
	Window.main()

#cProfile.run("profileEnvironment()", sort="cumtime")
cProfile.run("profileWindow()", sort="cumtime")
