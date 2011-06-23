import unittest
import math
import os
from particleswarm.swarm import Swarm
from particleswarm.particle import Particle
from particleswarm.fitness import Fitness

class Fitness1(Fitness):
	def calculateFitness(self, state):
		return abs(pow(state["x"], 3) + 0.5 * state["y"] - 20.5)

class Fitness2(Fitness):
	def calculateFitness(self, state):
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
		s1.setFitnessObject(Fitness1())
		self.assertTrue(s1.populate(25))
		self.assertEqual(len(s1.getParticles()), 25)

	def testRandomPopulation(self):
		s1 = Swarm()
		s1.setFitnessObject(Fitness1())
		s1.addDimension("x", -10, 10)
		s1.addDimension("y", -10, 10)
		self.assertTrue(s1.populate(25, "random"))
		self.assertEqual(len(s1.getParticles()), 25)

	def testRandomVelocityPopulation(self):
		s1 = Swarm()
		s1.setFitnessObject(Fitness1())
		s1.addDimension("x", 20, 40)
		s1.addDimension("y", -10, 10)
		self.assertTrue(s1.populate(25, initialVelocityMethod="random"))
		self.assertEqual(len(s1.getParticles()), 25)

	def testFindSolution(self):
		s1 = Swarm()
		s1.addDimension("x", -10, 10)
		s1.addDimension("y", -10, 10)
		s1.setFitnessObject(Fitness1())
		s1.populate(27)

		s1.findSolution(0.00001, 100)
		self.assertLessEqual(Fitness1().fitness(s1.getBestState()), 0.00001)

	def testFindSolution2(self):
		s1 = Swarm()
		s1.addDimension("x", -10, 10)
		s1.addDimension("y", -10, 10)
		s1.addDimension("z", -10, 10)
		s1.setFitnessObject(Fitness2())
		s1.populate(27)

		s1.findSolution(0.00001, 100)
		self.assertLessEqual(Fitness2().fitness(s1.getBestState()), 0.00001)

	def testDatabase(self):
		s1 = Swarm()
		s1.setDatabase("/tmp/psdatabasetest.db")
		self.assertTrue(os.path.exists("/tmp/psdatabasetest.db"))

		s1.addDimension("x", -10, 10)
		s1.addDimension("y", -10, 10)
		s1.setFitnessObject(Fitness1())
		s1.populate(27)

		s1.findSolution(5)

		del s1
		os.remove("/tmp/psdatabasetest.db")


	def testContinueDatabase(self):
		s1 = Swarm()
		s1.setDatabase("/tmp/psdatabasetest.db")
		self.assertTrue(os.path.exists("/tmp/psdatabasetest.db"))

		s1.addDimension("x", -10, 10)
		s1.addDimension("y", -10, 10)
		s1.setFitnessObject(Fitness1())
		s1.populate(10)

		s1.findSolution(5)

		del s1
		
		s3 = Swarm()
		self.assertRaises(ValueError, s3.setDatabase, "/tmp/psdatabasetest.db")
		
		s2 = Swarm()
		s2.setDatabase("/tmp/psdatabasetest.db", True)
		
		s2.addDimension("x", -10, 10)
		s2.addDimension("y", -10, 10)
		s2.setFitnessObject(Fitness1())
		s2.populate(10)

		s2.findSolution(5)

		del s2
		
		os.remove("/tmp/psdatabasetest.db")


	def testLoadFromDatabase(self):
		s1 = Swarm()
		s1.setDatabase("/tmp/psdatabasetest.db")

		s1.addDimension("x", -10, 10)
		s1.addDimension("y", -10, 10)
		s1.setFitnessObject(Fitness1())
		s1.populate(10)
		particleCount = len(s1.getParticles())
		s1.writeParticlesToDatabase(0)
		bestParticle0 = s1.getCurrentBestParticle()
		s1.step()
		s1.writeParticlesToDatabase(1)
		bestParticle1 = s1.getCurrentBestParticle()
		s1.step()
		s1.step()
		s1.writeParticlesToDatabase(3)
		bestParticle3 = s1.getCurrentBestParticle()
		s1.step()
		s1.writeParticlesToDatabase(4)
		bestParticle4 = s1.getCurrentBestParticle()
		del s1

		s2 = Swarm()
		s2.setFitnessObject(Fitness1())
		s2.loadParticlesFromDatabase("/tmp/psdatabasetest.db") # turn=-1

		self.assertEqual(bestParticle4.getVelocity(),
						 s2.getCurrentBestParticle().getVelocity())
		self.assertEqual(bestParticle4.getState(),
						 s2.getCurrentBestParticle().getState())
		self.assertEqual(particleCount, len(s2.getParticles()))
		del s2

		s3 = Swarm()
		s3.setFitnessObject(Fitness1())
		s3.loadParticlesFromDatabase("/tmp/psdatabasetest.db", -2)

		self.assertEqual(bestParticle3.getVelocity(),
						 s3.getCurrentBestParticle().getVelocity())
		self.assertEqual(bestParticle3.getState(),
						 s3.getCurrentBestParticle().getState())
		del s3

		s4 = Swarm()
		s4.setFitnessObject(Fitness1())
		s4.loadParticlesFromDatabase("/tmp/psdatabasetest.db", 1)

		self.assertEqual(bestParticle1.getVelocity(),
						 s4.getCurrentBestParticle().getVelocity())
		self.assertEqual(bestParticle1.getState(),
						 s4.getCurrentBestParticle().getState())
		del s4

		s5 = Swarm()
		s5.setFitnessObject(Fitness1())
		s5.loadParticlesFromDatabase("/tmp/psdatabasetest.db", 0)
		self.assertEqual(bestParticle0.getVelocity(),
						 s5.getCurrentBestParticle().getVelocity())
		self.assertEqual(bestParticle0.getState(),
						 s5.getCurrentBestParticle().getState())
		del s5

		os.remove("/tmp/psdatabasetest.db")


	def testGetBest(self):
		s1 = Swarm()
		self.assertEqual(s1.getCurrentBestParticle(), None)
		self.assertEqual(s1.getCurrentBestParticleFitness(), None)
		self.assertEqual(s1._Swarm__updateBestState(), None)
		self.assertEqual(s1.getBestFitness(), None)


	def testMultiProcessing(self):
		s1 = Swarm()
		s1.setNumberOfProcesses(2)
		s1.addDimension("x", -10, 10)
		s1.addDimension("y", -10, 10)
		s1.setFitnessObject(Fitness1())
		s1.populate(10)
		s1.getCurrentBestParticle()
		self.assertEqual(s1.getCurrentBestParticleFitness(), 15.5)
		s1.findSolution(0.00001, 100)
		self.assertLessEqual(Fitness1().fitness(s1.getBestState()), 0.00001)
