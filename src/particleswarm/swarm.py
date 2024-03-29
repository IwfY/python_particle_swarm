import copyreg
import types
from particleswarm.particle import Particle
from datetime import datetime, timezone
import math
import multiprocessing
import os
import random
import sqlite3


# code to make methods able to be used by pickle
# see http://bytes.com/topic/python/answers/552476-why-cant-you-pickle-instancemethods
def _pickle_method(method):
    func_name = method.__func__.__name__
    obj = method.__self__
    cls = method.__self__.__class__
    return _unpickle_method, (func_name, obj, cls)


def _unpickle_method(func_name, obj, cls):
    for cls in cls.mro():
        try:
            func = cls.__dict__[func_name]
        except KeyError:
            pass
        else:
            break
    return func.__get__(obj, cls)


copyreg.pickle(types.MethodType, _pickle_method, _unpickle_method)


class Swarm(object):
    """
    representation of the particle swarm
    """

    def __init__(self):
        self.__particles = []
        self.__dimensions = []
        self.__dimensionsDict = {}
        self.__bestState = None
        self.__bestStateFitness = None
        self.__fitnessObject = None
        self.__processes = 1		# number of processes
        self.__pool = None
        self.__iteration = 0
        self.__runName = datetime.now(timezone.utc).isoformat()

    def step(self):
        """
        update velocity of all particles and move them
        """
        for particle in self.__particles:
            particle.updateVelocity()
            particle.move()
        self.__updateBestState()
        self.__iteration += 1

    def resetSmallVelocities(self, maxVelocityLength):
        maxVelocityLengthSqr = maxVelocityLength * maxVelocityLength

        for particle in self.__particles:
            if particle.getSqrVelocityVectorLength() < maxVelocityLengthSqr:
                newVelocity = {}
                for dimension in self.__dimensions:
                    newVelocity[dimension[0]] = random.uniform(-(dimension[2] - dimension[1]) / 2, (dimension[2] - dimension[1]) / 2)
                particle.setVelocity(newVelocity)

                newState = {}
                for dimension in self.__dimensions:
                    newState[dimension[0]] = random.uniform(dimension[1], dimension[2])
                particle.setState(newState)

    def getFitnessObject(self):
        return self.__fitnessObject

    def setFitnessObject(self, fitnessObject):
        """
        set fitness object and propagate to particles
        """
        self.__fitnessObject = fitnessObject
        for particle in self.__particles:
            particle.setFitnessObject(fitnessObject)

    def setParticleVelcityUpdateStrategyObject(self, particleVelocityUpdateStrategy):
        """
        set fitness object and propagate to particles
        """
        self.__particleVelocityUpdateStrategy = particleVelocityUpdateStrategy
        for particle in self.__particles:
            particle.setVelcityUpdateStrategyObject(particleVelocityUpdateStrategy)

    def loadParticlesFromDatabase(self, database, turn=-1):
        """Delete all particles, populate swarm from particle states in
        a given turn from the database

        Attention: the output database is not set to the given database

        @param database the path to the database
        @param turn the turn from which the particle data should be
        choosen, if a negative value is given count backwards (e.g.
        turn = -2 means the second last turn)
        """
        self.__particles = []

        try:
            inputDatabase = sqlite3.connect(database)
            cur = inputDatabase.cursor()
        except Exception:
            pass

        if turn < 0:
            cur.execute("SELECT MAX(iteration) FROM particle_state")
            queryParameters = (int(cur.fetchone()[0]) + turn + 1,)
        else:
            queryParameters = (turn,)

        cur.execute("""SELECT state, velocity
					   FROM particle_state
					   WHERE iteration = ?
					   ORDER BY id""",
                    queryParameters)

        #result = cur.fetchall()

        for particle in cur:
            self.__particles.append(Particle(eval(particle[0]),
                                             eval(particle[1]),
                                             self.__fitnessObject))

        inputDatabase.close()

        self.__updateBestState()

    def populate(self, particleCount=100, distribution="uniform", initialVelocityMethod="zero"):
        """
        initialize particles that are spread over the problem space

        valid distribution mathods are:
                                        uniform
                                        random
                                        uniform_fill_random
                                        random_magnet_border ... if value is within 10% next to min/max value of dimension it is set to that

        valid mathods to initialize the velocity of a particle
                                        zero		velocity is zero
                                        random		velocity is a random vector
        """

        if self.dimensionCount() == 0:
            return False

        if particleCount < 1:
            return False

        initialStates = []

        if distribution == "uniform" or distribution == "uniform_fill_random":
            particlesPerDimension = int(math.floor(math.pow(particleCount, 1 / self.dimensionCount())))
            if particlesPerDimension < 2:
                return False

            initialStates.append({})
            for dimension in self.__dimensions:
                stepPerState = (dimension[2] - dimension[1]) / (particlesPerDimension - 1)
                tmpStates = []
                rmStates = []
                for state in initialStates:
                    for i in range(particlesPerDimension):
                        tmpState = state.copy()
                        tmpState[dimension[0]] = dimension[1] + i * stepPerState
                        tmpStates.append(tmpState)
                        # end for i in range(particlesPerDimension)

                    rmStates.append(state)
                    # end for state in initialStates

                for state in rmStates:
                    initialStates.remove(state)

                initialStates.extend(tmpStates)
                # end for dimension in self.__dimensions
        elif distribution == "random":
            random.seed()
            for i in range(particleCount):
                tmpState = {}
                for dimension in self.__dimensions:
                    tmpState[dimension[0]] = random.uniform(dimension[1], dimension[2])
                initialStates.append(tmpState.copy())

        elif distribution == "random_magnet_border":
            random.seed()
            for i in range(particleCount):
                tmpState = {}
                for dimension in self.__dimensions:
                    randomValue = random.uniform(dimension[1], dimension[2])

                    dimensionTenth = (dimension[2] - dimension[1]) / 10
                    if randomValue - dimensionTenth < dimension[1]:
                        randomValue = dimension[1]
                    elif randomValue + dimensionTenth > dimension[2]:
                        randomValue = dimension[2]

                    tmpState[dimension[0]] = randomValue

                initialStates.append(tmpState.copy())

        elif distribution == "random_best_of_10":
            if self.__fitnessObject is None:
                return False
            random.seed()
            for i in range(particleCount):
                bestState = None
                bestStateFitness = None
                for i in range(10):
                    tmpState = {}
                    for dimension in self.__dimensions:
                        tmpState[dimension[0]] = random.uniform(dimension[1], dimension[2])

                    if i == 0:
                        bestState = tmpState
                        bestStateFitness = self.__fitnessObject.fitness(tmpState)
                        continue

                    currentFitness = self.__fitnessObject.fitness(tmpState)
                    if currentFitness < bestStateFitness:
                        bestState = tmpState
                        bestStateFitness = currentFitness

                initialStates.append(bestState.copy())

        if distribution == "uniform_fill_random":
            for i in range(len(initialStates), particleCount):
                tmpState = {}
                for dimension in self.__dimensions:
                    tmpState[dimension[0]] = random.uniform(dimension[1], dimension[2])
                initialStates.append(tmpState.copy())

        if initialVelocityMethod == "zero":
            velocity = {}
            for dimension in self.__dimensions:
                velocity[dimension[0]] = 0.0

            for state in initialStates:
                self.__particles.append(Particle(state, velocity.copy(), self.__fitnessObject, self.__particleVelocityUpdateStrategy))
        elif initialVelocityMethod == "random" or initialVelocityMethod == "random_10th":
            random.seed()
            multiplier = 1
            if initialVelocityMethod == "random_10th":
                multiplier = 0.1

            for state in initialStates:
                velocity = {}
                for dimension in self.__dimensions:
                    velocity[dimension[0]] = random.uniform(-(dimension[2] - dimension[1]) / 2, (dimension[2] - dimension[1]) / 2) * multiplier
                self.__particles.append(Particle(state, velocity.copy(), self.__fitnessObject, self.__particleVelocityUpdateStrategy))

        self.__updateBestState()
        return True

    def injectParticleState(self, state, index=0):
        if index > len(self.__particles) - 1:
            return

        self.__particles[index].setState(state)
        self.__updateBestState(noCache=True)

    def getMinPopulationForUniformDistribution(self):
        return pow(2, len(self.getDimensions()))

    def addDimension(self, name, lowerLimit=0.0, upperLimit=1.0):
        """
        add a dimension to the problem space
        """
        if self.hasDimension(name):
            return False

        if lowerLimit > upperLimit:
            return False

        self.__dimensions.append((name, float(lowerLimit), float(upperLimit)))
        self.__dimensionsDict[name] = {'min': float(lowerLimit), 'max': float(upperLimit)}
        return True

    def dimensionCount(self):
        return len(self.__dimensions)

    def getDimensions(self):
        return self.__dimensions

    def hasDimension(self, dimensionName):
        for (name, lower, upper) in self.__dimensions:
            if name == dimensionName:
                return True
        return False

    def getDimensionsDict(self):
        return self.__dimensionsDict

    def getDimensionRangeSum(self):
        sum = 0.0
        for dimension in self.getDimensions():
            sum += dimension[2] - dimension[1]
        return sum

    def getNumberOfProcesses(self):
        return self.__processes

    def setNumberOfProcesses(self, processes):
        assert(processes > 0)
        self.__processes = processes

        if processes > 1:
            self.__pool = multiprocessing.Pool(processes)
        else:
            self.__pool = None

    def getParticles(self):
        return self.__particles

    def getRunName(self):
        return self.__runName

    def getCurrentBestParticle(self):
        if not self.__particles:
            return None

        if self.__pool:
            stateList = []
            for particle in self.__particles:
                stateList.append(particle.getState())
            fitnessList = self.__pool.map(self.__fitnessObject.fitness, stateList)
            minFitness = min(fitnessList)
            listIndexOfMin = fitnessList.index(minFitness)

            return self.__particles[listIndexOfMin]
        else:
            bestParticle = self.__particles[0]
            lowestFitness = bestParticle.fitness()

            for particle in self.__particles:
                currentFitness = particle.fitness()
                if currentFitness < lowestFitness:
                    bestParticle = particle
                    lowestFitness = currentFitness

            return bestParticle

    def getCurrentBestParticleFitness(self):
        bestParticle = self.getCurrentBestParticle()
        if bestParticle == None:
            return None

        return bestParticle.fitness()

    def __updateBestState(self, noCache=False):
        if not self.__particles:
            return None

        if self.__bestState == None or noCache == True:
            particle = self.getCurrentBestParticle()
            self.__bestState = particle.getState().copy()
            self.__bestStateFitness = particle.fitness()
        else:
            particle = self.getCurrentBestParticle()
            fitness = particle.fitness()
            if fitness < self.__bestStateFitness:
                self.__bestState = particle.getState().copy()
                self.__bestStateFitness = particle.fitness()

    def getBestFitness(self):
        """
        get the fitness of the historical best known state
        """
        if self.__fitnessObject == None or self.__bestState == None:
            return None

        return self.__bestStateFitness

    def getMeanFitness(self):
        fitnesses = [particle.fitness() for particle in self.getParticles()]
        fitnesses.sort()
        return fitnesses[len(fitnesses) // 2]

    def getAverageFitness(self):
        sum = 0.0
        for particle in self.getParticles():
            sum += particle.fitness()

        return sum / len(self.getParticles())

    def getBestState(self):
        return self.__bestState

    def getIteration(self):
        return self.__iteration

    def getDimensionNormalizedParticleState(self, particle):
        normalizedState = {}
        for key, value in particle.getState().items():
            normalizedState[key] = (value - self.getDimensionsDict()[key]['min']) / (self.getDimensionsDict()[key]['max'] - self.getDimensionsDict()[key]['min'])

        return normalizedState

    def getNormalizedAverageDistanceToParticleNearestNeighbour(self):
        normalizedStates = {}
        sumOfDistances = 0.0
        for particle in self.getParticles():
            particleState = None
            if particle.getId() in normalizedStates:
                particleState = normalizedStates[particle.getId()]
            else:
                particleState = self.getDimensionNormalizedParticleState(particle)
                normalizedStates[particle.getId()] = particleState
            minDistance = None

            # get distance to nearest neighbour normalized for dimension range and dimension count
            for subParticle in self.getParticles():
                if particle == subParticle:
                    continue

                subParticleState = None
                if subParticle.getId() in normalizedStates:
                    subParticleState = normalizedStates[subParticle.getId()]
                else:
                    subParticleState = self.getDimensionNormalizedParticleState(subParticle)
                    normalizedStates[subParticle.getId()] = subParticleState

                distance = 0.0
                for key in particleState.keys():
                    distance += abs(particleState[key] - subParticleState[key])
                distance /= len(self.getDimensions())
                if minDistance is None:
                    minDistance = distance
                    continue

                minDistance = min(minDistance, distance)
            sumOfDistances += minDistance

        return sumOfDistances / len(self.getParticles())

    def getNormalizedMeanDistanceToParticleNearestNeighbour(self):
        normalizedStates = {}
        normalizedDistances = []
        for particle in self.getParticles():
            particleState = None
            if particle.getId() in normalizedStates:
                particleState = normalizedStates[particle.getId()]
            else:
                particleState = self.getDimensionNormalizedParticleState(particle)
                normalizedStates[particle.getId()] = particleState
            minDistance = None

            # get distance to nearest neighbour normalized for dimension range and dimension count
            for subParticle in self.getParticles():
                if particle == subParticle:
                    continue

                subParticleState = None
                if subParticle.getId() in normalizedStates:
                    subParticleState = normalizedStates[subParticle.getId()]
                else:
                    subParticleState = self.getDimensionNormalizedParticleState(subParticle)
                    normalizedStates[subParticle.getId()] = subParticleState

                distance = 0.0
                for key in particleState.keys():
                    distance += abs(particleState[key] - subParticleState[key])
                distance /= len(self.getDimensions())
                if minDistance is None:
                    minDistance = distance
                    continue

                minDistance = min(minDistance, distance)
            normalizedDistances.append(minDistance)

        normalizedDistances.sort()

        return normalizedDistances[len(normalizedDistances) // 2]
