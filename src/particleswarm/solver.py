import math
from particleswarm.default_particle_velocity_update_strategy import DefaultParticleVelocityUpdateStrategy
from particleswarm.particle_velocity_update.mutation_decorator import MutationDecorator
from particleswarm.swarm import Swarm
from particleswarm.swarm_elasticsearch_exporter import SwarmElasticsearchExporter

class ParticleSwarmSolver(object):
	"""
	representation of a problem to be solved by a particle swarm
	"""

	def __init__(self, problemName, fitnessObject, dimensions, populationInformation = [128, "random", "random"], particleVelocityUpdateStrategy=None):
		self.__problemName = problemName
		self.__fitnessObject = fitnessObject
		self.__dimensions = dimensions
		self.__populationCount, self.__initDistributionMethod, self.__initVelocityMethod = populationInformation
		self.__swarmElasticsearchExporter = None

		self.__swarm = Swarm()
		self.__swarm.setFitnessObject(self.__fitnessObject)

		if particleVelocityUpdateStrategy is not None:
			self.__swarm.setParticleVelcityUpdateStrategyObject(particleVelocityUpdateStrategy)
		else:
			particleVelocityUpdateStrategy = DefaultParticleVelocityUpdateStrategy(self.__swarm, 0.6, 0.3, 0.3, 0.3)
			decoratedParticleVelocityUpdateStrategy = MutationDecorator(\
				particleVelocityUpdateStrategy, velocityMutationThreshold=len(self.__dimensions) / 2, mutationFactor=2000, mutationNumber=len(self.__dimensions) // 4)
			self.__swarm.setParticleVelcityUpdateStrategyObject(decoratedParticleVelocityUpdateStrategy)

		for dimensionsName, dimnesionMin, dimensionMax in dimensions:
			self.__swarm.addDimension(dimensionsName, dimnesionMin, dimensionMax)

		self.__swarm.populate(self.__populationCount, self.__initDistributionMethod, self.__initVelocityMethod)

	def setElasticSearchServer(self, serverBaseUrl, indexName, fitnessThreshold=100000, historicBestOnly=False, minTurn=None):
		self.__swarmElasticsearchExporter = SwarmElasticsearchExporter(serverBaseUrl, indexName, fitnessThreshold, historicBestOnly, minTurn)

	def getSwarm(self):
		return self.__swarm

	def printState(self, state):
		strings = []
		for key in state.keys():
			strings.append('{}: {:10.4f}'.format(key, state[key]))

		print(', '.join(strings))

	def solve(self, iterations, targetFitness=None, postStepFunctions=[]):
		print('##############################################################')
		print('Population: {}'.format(len(self.__swarm.getParticles())))
		print('Fitness function: {}'.format(self.__swarm.getFitnessObject().getName()))

		currentBestParticle = self.__swarm.getCurrentBestParticle()
		currentBestState = currentBestParticle.getState()
		currentBestFitness = self.__swarm.getCurrentBestParticleFitness()
		print('~~~~~~~ 0/' + str(iterations) + ' ~~~~~~~~~~~~~~~~~~~')
		print('Id: ' + str(currentBestParticle.getId()))
		self.printState(currentBestState)
		print("Fitness : {:15,.2f}    |    Velo length : {:15,.2f}".format(currentBestFitness, math.sqrt(currentBestParticle.getSqrVelocityVectorLength())))
		if self.__swarmElasticsearchExporter is not None:
			self.__swarmElasticsearchExporter.writeParticles(swarm=self.getSwarm(), turn=0)

		lastGlobalBestFitness = currentBestFitness
		for i in range(1, iterations + 1):
			self.__swarm.step()

			if self.__swarmElasticsearchExporter is not None:
				self.__swarmElasticsearchExporter.writeParticles(swarm=self.getSwarm(), turn=i)

			currentBestParticle = self.__swarm.getCurrentBestParticle()
			currentBestState = currentBestParticle.getState()
			currentBestFitness = self.__swarm.getCurrentBestParticleFitness()
			print('~~~~~~~ ' + str(i) + '/' + str(iterations) + ' ~~~~~~~~~~~~~~~~~~~')
			print('Id: ' + str(currentBestParticle.getId()))
			self.printState(currentBestState)
			if (currentBestFitness < lastGlobalBestFitness):
				print("Fitness : {:15,.2f}  ({:12,.3f})  |    Velo length : {:12,.3f}"
					.format(currentBestFitness, -(lastGlobalBestFitness - currentBestFitness), math.sqrt(currentBestParticle.getSqrVelocityVectorLength())))
				lastGlobalBestFitness = currentBestFitness
			else:
				print("Fitness : {:15,.2f}    |    Velo length : {:15,.2f}".format(currentBestFitness, math.sqrt(currentBestParticle.getSqrVelocityVectorLength())))

			for postStepFunction in postStepFunctions:
				postStepFunction(swarm=self.__swarm, iteration=i, iterationCount=iterations)

			if targetFitness is not None and currentBestFitness <= targetFitness:
				break

		return [self.__swarm.getBestState(), self.__swarm.getBestFitness()]
