import cProfile
from Environment import *

def main():
	environment = Environment()
	environment.createHerd(100)
	n = 0
	while n < 100:
		environment.update(1/1000)
		n += 1

cProfile.run("main()", sort="cumulative")