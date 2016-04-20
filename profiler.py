import cProfile

def profileEnvironment():
	import Vector
	import Creature
	import Herd
	import Environment
	environment = Environment.Environment()
	environment.createHerd(20)
	for n in range(100):
		environment.update(1/100)

def profileWindow():
	from Main import main
	main()

#cProfile.run("profileEnvironment()", sort="cumtime")
cProfile.run("profileWindow()", sort="cumtime")
