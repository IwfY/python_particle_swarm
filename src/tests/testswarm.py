import unittest
import math
from particleswarm.swarm import Swarm
from particleswarm.fitness import Fitness

class Fitness1(Fitness):
	def fitness(self, state):
		return abs(pow(state["x"], 3) + 0.5 * state["y"] - 20.5)

class Fitness2(Fitness):
	def fitness(self, state):
		return abs(pow(state["x"], 3) + 0.5 * state["y"] - 20.5 + math.log(abs(state["z"] + 1)))


class TestSwarm(unittest.TestCase):
	def testDimensions(self):
		s1 = Swarm()
		self.assertEqual(s1.getDimensions(), [])

		s1.addDimension("x", -10, 10)
		self.assertEqual(s1.getDimensions()[0], ("x", -10, 10))

		s1.addDimension("x", -10, 10)
		self.assertEqual(len(s1.getDimensions()), 1)

		s1.addDimension("y", -5, 5)
		self.assertEqual(s1.getDimensions()[1], ("y", -5, 5))
		self.assertEqual(len(s1.getDimensions()), 2)

		self.assertEqual(len(s1.getDimensions()), s1.dimensionCount())

	def testPopulate(self):
		s1 = Swarm()
		self.assertFalse(s1.populate())
		self.assertEqual(len(s1.getParticles()), 0)

		s1.addDimension("x", -10, 10)
		s1.addDimension("y", -10, 10)
		self.assertFalse(s1.populate())
		self.assertEqual(len(s1.getParticles()), 0)

		s1.setFitnessObject(Fitness1())
		self.assertTrue(s1.populate(25))
		self.assertEqual(len(s1.getParticles()), 25)

	def testFindSolution(self):
		s1 = Swarm()
		s1.addDimension("x", -10, 10)
		s1.addDimension("y", -10, 10)
		s1.setFitnessObject(Fitness1())
		s1.populate(27)

		s1.findsolution(0.00001, 100)
		self.assertLessEqual(Fitness1().fitness(s1.getBestState()), 0.00001)

	def testFindSolution2(self):
		s1 = Swarm()
		s1.addDimension("x", -10, 10)
		s1.addDimension("y", -10, 10)
		s1.addDimension("z", -10, 10)
		s1.setFitnessObject(Fitness2())
		s1.populate(27)

		s1.findsolution(0.00001, 100)
		self.assertLessEqual(Fitness2().fitness(s1.getBestState()), 0.00001)

