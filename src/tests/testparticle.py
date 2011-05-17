import unittest
from particleswarm.particle import Particle
from particleswarm.fitness import Fitness

class Fitness1(Fitness):
	def calculateFitness(self, state):
		return abs(state["x"] + state["y"] - 5)
		

class TestNeuron(unittest.TestCase):
	def testMove(self):
		p1 = Particle({"x": 0.0, "y": 0.0}, {"x": 0.0, "y": 0.0}, Fitness1())
		p1._Particle__velocity = ({"x": 1.0, "y": 1.0})
		p1.move()
		self.assertEqual(p1.getState()["x"], 1.0)
		self.assertEqual(p1.getState()["y"], 1.0)

		p1._Particle__velocity = ({"x": 1.0, "y": -2.0})
		p1.move()
		self.assertEqual(p1.getState()["x"], 2.0)
		self.assertEqual(p1.getState()["y"], -1.0)

	def testBestState(self):
		f = Fitness1()
		p1 = Particle({"x": 0.0, "y": 0.0}, {"x": 0.0, "y": 0.0}, f)
		self.assertEqual(p1.fitness(), 5.0)
		self.assertEqual(p1.getBestState()["x"], 0.0)
		self.assertEqual(p1.getBestState()["y"], 0.0)
		
		p1.updateVelocity({"x": 1.0, "y": 1.0}, 1.0, 0.0, 1.0, 0.0)
		p1.move()
		self.assertEqual(p1.fitness(), 3.0)
		self.assertEqual(p1.getBestState()["x"], 1.0)
		self.assertEqual(p1.getBestState()["y"], 1.0)
		
		p1.updateVelocity({"x": 10.0, "y": 10.0}, 1.0, 0.0, 1.0, 0.0)
		p1.move()
		self.assertEqual(p1.fitness(), 15.0)
		self.assertEqual(p1.getBestState()["x"], 1.0)
		self.assertEqual(p1.getBestState()["y"], 1.0)		

	def testUpdateVelocity(self):
		p1 = Particle({"x": 0.0, "y": 0.0}, {"x": 0.0, "y": 0.0}, Fitness1())
		self.assertEqual(p1.getVelocity()["x"], 0.0)
		self.assertEqual(p1.getVelocity()["y"], 0.0)
		p1.resetVelocity()

		p1.updateVelocity({"x": 0.0, "y": 0.0}, 1.0, 1.0, 1.0, 1.0)
		self.assertEqual(p1.getVelocity()["x"], 0.0)
		self.assertEqual(p1.getVelocity()["y"], 0.0)

		p1._Particle__bestState = ({"x": 1.0, "y": 1.0})
		p1._Particle__velocity = ({"x": 1.0, "y": 1.0})
		p1.updateVelocity({"x": 1.0, "y": 1.0}, 1.0, 1.0, 1.0, 1.0)
		self.assertEqual(p1.getVelocity()["x"], 3.0)
		self.assertEqual(p1.getVelocity()["y"], 3.0)

		p1._Particle__bestState = ({"x": 1.0, "y": 1.0})
		p1._Particle__velocity = ({"x": 1.0, "y": 1.0})
		p1.updateVelocity({"x": 1.0, "y": 1.0}, 0.5, 1.0, 1.0, 1.0)
		self.assertEqual(p1.getVelocity()["x"], 1.5)
		self.assertEqual(p1.getVelocity()["y"], 1.5)

		p1._Particle__bestState = ({"x": 1.0, "y": -1.0})
		p1._Particle__velocity = ({"x": 1.0, "y": -1.0})
		p1.updateVelocity({"x": 1.0, "y": -1.0}, 0.5, 1.0, 1.0, 1.0)
		self.assertEqual(p1.getVelocity()["x"], 1.5)
		self.assertEqual(p1.getVelocity()["y"], -1.5)

	def testUpdateVelocityGlobalBest(self):
		p1 = Particle({"x": 0.0, "y": 0.0}, {"x": 0.0, "y": 0.0}, Fitness1())

		# global best is at 1.0, 1.0
		p1.updateVelocity({"x": 1.0, "y": 1.0}, 1.0, 0.0, 1.0, 0.0)
		self.assertEqual(p1.getVelocity()["x"], 1.0)
		self.assertEqual(p1.getVelocity()["y"], 1.0)
		p1.resetVelocity()

		p1.updateVelocity({"x": -1.0, "y": -1.0}, 1.0, 0.0, 1.0, 0.0)
		self.assertEqual(p1.getVelocity()["x"], -1.0)
		self.assertEqual(p1.getVelocity()["y"], -1.0)
		p1.resetVelocity()

		p1.updateVelocity({"x": 1.0, "y": 1.0}, 1.0, 0.0, 0.5, 0.0)
		self.assertEqual(p1.getVelocity()["x"], 0.5)
		self.assertEqual(p1.getVelocity()["y"], 0.5)
		p1.resetVelocity()

		p1.updateVelocity({"x": 1.0, "y": 1.0}, 0.5, 0.0, 0.5, 0.0)
		self.assertEqual(p1.getVelocity()["x"], 0.25)
		self.assertEqual(p1.getVelocity()["y"], 0.25)
		p1.resetVelocity()

	def testUpdateVelocityLocalBest(self):
		p1 = Particle({"x": 0.0, "y": 0.0}, {"x": 0.0, "y": 0.0}, Fitness1())
		p1._Particle__bestState = ({"x": 1.0, "y": 1.0})
		self.assertEqual(p1.getBestState()["x"], 1.0)
		self.assertEqual(p1.getBestState()["y"], 1.0)

		# local best is at 1.0, 1.0
		p1.updateVelocity({"x": 0.0, "y": 0.0}, 1.0, 0.0, 0.0, 1.0)
		self.assertEqual(p1.getVelocity()["x"], 1.0)
		self.assertEqual(p1.getVelocity()["y"], 1.0)
		p1.resetVelocity()

		p1._Particle__bestState = ({"x": -1.0, "y": -1.0})
		p1.updateVelocity({"x": 0.0, "y": 0.0}, 1.0, 0.0, 0.0, 1.0)
		self.assertEqual(p1.getVelocity()["x"], -1.0)
		self.assertEqual(p1.getVelocity()["y"], -1.0)
		p1.resetVelocity()

		p1._Particle__bestState = ({"x": 1.0, "y": 1.0})
		p1.updateVelocity({"x": 0.0, "y": 0.0}, 1.0, 0.0, 0.0, 0.5)
		self.assertEqual(p1.getVelocity()["x"], 0.5)
		self.assertEqual(p1.getVelocity()["y"], 0.5)
		p1.resetVelocity()

		p1._Particle__bestState = ({"x": 1.0, "y": 1.0})
		p1.updateVelocity({"x": 0.0, "y": 0.0}, 0.5, 0.0, 0.0, 0.5)
		self.assertEqual(p1.getVelocity()["x"], 0.25)
		self.assertEqual(p1.getVelocity()["y"], 0.25)
		p1.resetVelocity()

	def testUpdateVelocityOldVelocity(self):
		p1 = Particle({"x": 0.0, "y": 0.0}, {"x": 0.0, "y": 0.0}, Fitness1())
		p1._Particle__velocity = ({"x": 1.0, "y": 1.0})
		self.assertEqual(p1.getVelocity()["x"], 1.0)
		self.assertEqual(p1.getVelocity()["y"], 1.0)

		p1.updateVelocity({"x": 0.0, "y": 0.0}, 1.0, 1.0, 0.0, 0.0)
		self.assertEqual(p1.getVelocity()["x"], 1.0)
		self.assertEqual(p1.getVelocity()["y"], 1.0)

		p1._Particle__velocity = ({"x": 1.0, "y": 1.0})
		p1.updateVelocity({"x": 0.0, "y": 0.0}, 1.0, 0.5, 0.0, 0.0)
		self.assertEqual(p1.getVelocity()["x"], 0.5)
		self.assertEqual(p1.getVelocity()["y"], 0.5)

		p1._Particle__velocity = ({"x": 1.0, "y": 1.0})
		p1.updateVelocity({"x": 0.0, "y": 0.0}, 0.5, 0.5, 0.0, 0.0)
		self.assertEqual(p1.getVelocity()["x"], 0.25)
		self.assertEqual(p1.getVelocity()["y"], 0.25)
