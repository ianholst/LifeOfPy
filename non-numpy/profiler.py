import cProfile

def profileEnvironment():
	import Vector
	import Creature
	import Environment
	environment = Environment.Environment(gridSize=32, cellSize=10, terrainResolution=128)
	environment.createHerd(50)
	for n in range(1000):
		environment.update(1/100)

def profileWindow():
	from Main import main
	main()

cProfile.run("profileEnvironment()", sort="cumtime")
#cProfile.run("profileWindow()", sort="cumtime")