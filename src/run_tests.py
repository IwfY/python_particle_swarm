import unittest
from tests import *

if __name__ == '__main__':
	suite = unittest.TestSuite()

	suite.addTest(unittest.TestLoader().loadTestsFromModule(testfitness))
	suite.addTest(unittest.TestLoader().loadTestsFromModule(testparticle))
	suite.addTest(unittest.TestLoader().loadTestsFromModule(testswarm))

	unittest.TextTestRunner(verbosity=1).run(suite)
