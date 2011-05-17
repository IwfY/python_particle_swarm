import unittest
from particleswarm.fitness import Fitness

class TestFitness(unittest.TestCase):
	def testStateToTuple(self):
		state = {'x': 4.5, 'y': 3.33, 'ab': 17.44}
		tuple = ('ab', 17.44, 'x', 4.5, 'y', 3.33)
		self.assertEqual(Fitness.stateToTuple(state), tuple)

	def testBuffer(self):
		state1 = {'x': 4.5, 'y': 3.33, 'ab': 17.44}
		state1s = {'ab': 17.44, 'x': 4.5, 'y': 3.33}
		state2 = {'v': 4.6, 'w': 44.33, 'ab': 17.44}

		f = Fitness()
		f._Fitness__addFitnessToBuffer(state1, 2.0)
		f._Fitness__addFitnessToBuffer(state1, 1.0)
		self.assertEqual(f._Fitness__getBufferedFitness(state1), 1.0)
		self.assertEqual(f._Fitness__getBufferedFitness(state1s), 1.0)
		self.assertEqual(f._Fitness__getBufferedFitness(state2), None)
		self.assertEqual(len(f._Fitness__buffer), 1)
		f._Fitness__addFitnessToBuffer(state2, 1.5)
		self.assertEqual(f._Fitness__getBufferedFitness(state2), 1.5)
		self.assertEqual(len(f._Fitness__buffer), 2)
