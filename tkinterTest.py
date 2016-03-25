from Creature import Creature
import random
from Vector import Vector, mag, unit

creatureList = []
N = 50
for n in range(N):
	creatureList += [Creature(age=0, energy=100, size=10, pos=Vector(1000*random.random(),1000*random.random()) )]

k = -1
def calculateForces():
	for creature in creatureList:
		creature.netForce = Vector(0,0)
		for otherCreature in creatureList:
			if otherCreature != creature:
				creature.netForce += k / mag(creature.pos - otherCreature.pos)**1 * unit(creature.pos - otherCreature.pos)

from tkinter import *
root = Tk()
canvas = Canvas(root, width=1000, height=1000, background="black")
canvas.pack()

selectedCreature = None

def mousePressed(event):
	global selectedCreature
	for creature in creatureList:
		if (creature.pos.x - creature.size <= event.x <= creature.pos.x + creature.size and
			creature.pos.y - creature.size <= event.y <= creature.pos.y + creature.size):
			selectedCreature = creature
			break
	canvas.update()

def mouseMoved(event):
	global selectedCreature
	if selectedCreature != None:
		selectedCreature.pos = Vector(event.x, event.y)
		selectedCreature.vel = Vector(0,0)
	canvas.update()

def mouseReleased(event):
	global selectedCreature
	if selectedCreature != None:
		selectedCreature = None
	canvas.update()

canvas.bind("<ButtonPress-1>", lambda event: mousePressed(event))
canvas.bind("<B1-Motion>", lambda event: mouseMoved(event))
canvas.bind("ButtonRelease-1>", lambda event: mouseReleased(event)) # Doesn't work for some reason

def timerFired():
	canvas.delete(ALL)
	calculateForces()
	if selectedCreature != None:
		canvas.create_rectangle(selectedCreature.pos.x-selectedCreature.size, selectedCreature.pos.y-selectedCreature.size, 
			selectedCreature.pos.x+selectedCreature.size, selectedCreature.pos.y+selectedCreature.size, outline="red")
	for creature in creatureList:
		creature.takeStep()
		canvas.create_oval(creature.pos.x-creature.size, creature.pos.y-creature.size, 
			creature.pos.x+creature.size, creature.pos.y+creature.size, fill="white")
	canvas.update()
	canvas.after(10, timerFired)
timerFired()
root.mainloop()