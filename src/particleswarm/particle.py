class Particle(object):
    '''
    class represents a single particle
    '''

    __lastId = 1

    def __init__(self, state, velocity, fitnessObject, particleVelocityUpdateStrategy):
        self.__id = Particle.__lastId
        Particle.__lastId += 1
        self.__state = state
        self.__bestState = state.copy()
        self.__bestStateFitness = None
        self.__velocity = velocity
        self.__fitnessObject = fitnessObject
        self.__particleVelocityUpdateStrategy = particleVelocityUpdateStrategy
        self.__cachedFitness = None

    def getFitness(self):
        '''
        returns the fitness of the particle
        '''
        if self.__cachedFitness is not None:
            return self.__cachedFitness

        self.__cachedFitness = self.__fitnessObject.fitness(self.__state)
        return self.__cachedFitness

    def fitness(self):
        return self.getFitness()

    def setVelcityUpdateStrategyObject(self, particleVelocityUpdateStrategy):
        """
        set fitness object and propagate to particles
        """
        self.__particleVelocityUpdateStrategy = particleVelocityUpdateStrategy

    def move(self):
        '''
        move according to velocity and update own best state
        '''
        if self.__fitnessObject == None:
            return False

        for key in self.__state.keys():
            self.__state[key] = self.__state[key] + self.__velocity[key]

        # reset fitness cache
        self.__cachedFitness = None

        self.updateBestState()

        return True

    def updateVelocity(self):
        '''
        recalculate the velocity
        '''
        self.__velocity = self.__particleVelocityUpdateStrategy.getNewVelocity(self)

    def setVelocity(self, velocity):
        self.__velocity = velocity

    def getSqrVelocityVectorLength(self):
        out = 0
        for key in self.__velocity.keys():
            out += self.__velocity[key] * self.__velocity[key]

        return out

    def getId(self):
        return self.__id

    def getState(self):
        return self.__state

    def setState(self, state):
        self.__state = state.copy()
        self.__cachedFitness = None
        self.__bestStateFitness = None
        self.resetLocalBest()
        self.updateBestState()

    def getBestState(self):
        return self.__bestState

    def updateBestState(self):
        # update local best fitness
        currentFitness = self.fitness()
        if currentFitness < self.getBestStateFitness():
            self.__bestState = self.__state.copy()
            self.__bestStateFitness = currentFitness

    def getBestStateFitness(self):
        if self.__bestStateFitness is not None:
            return self.__bestStateFitness

        self.__bestStateFitness = self.__fitnessObject.fitness(self.__bestState)
        return self.__bestStateFitness

    def setFitnessObject(self, fitnessObject):
        self.__fitnessObject = fitnessObject

    def getVelocity(self):
        return self.__velocity

    def resetVelocity(self):
        for key in self.__velocity.keys():
            self.__velocity[key] = 0.0

    def resetLocalBest(self):
        self.__localBest = self.__state.copy()
