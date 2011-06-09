from particleswarm import *
import profile

class Fitness1(fitness.Fitness):
	def calculateFitness(self, state):
		return abs(pow(state["x"], 3) + 0.5 * state["y"] - 20.5)

if __name__ == '__main__':
	s = swarm.Swarm()
	s.addDimension("x", -10, 10)
	s.addDimension("y", -10, 10)
	s.setFitnessObject(Fitness1())
	s.populate(100)
	profile.run("s.findSolution(0.0, 10)")
