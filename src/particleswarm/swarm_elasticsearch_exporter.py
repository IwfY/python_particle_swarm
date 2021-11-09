import json
import math
import requests


class SwarmElasticsearchExporter(object):
    def __init__(self, server, indexName, fitnessThreshold=100000, historicBestOnly=False, minTurn=None):
        self.__server = server
        self.__indexName = indexName
        self.__fitnessThreshold = fitnessThreshold
        self.__historicBestOnly = historicBestOnly
        self.__minTurn = minTurn
        self.__bulkUrl = '{}/{}/_doc/_bulk'.format(self.__server, self.__indexName)

    def writeParticles(self, swarm, turn):
        """
        writes data about particles to Elastic Search
        """
        if self.__minTurn is not None and turn < self.__minTurn:
            return

        currentBestPartice = swarm.getCurrentBestParticle()
        historicBestFitness = swarm.getBestFitness()

        requestPayLoad = ""
        for particle in swarm.getParticles():
            out = {}
            out['runName'] = swarm.getRunName()
            out['particle'] = particle.getId()
            out['turn'] = turn
            out['fitness'] = float(particle.fitness())
            out['isCurrentBest'] = int(particle == currentBestPartice)
            if out['fitness'] > self.__fitnessThreshold and out['isCurrentBest'] != 1:
                continue
            out['isHistoricBest'] = int(out['fitness'] == historicBestFitness)
            if self.__historicBestOnly == True and out['isHistoricBest'] == False:
                continue
            out['fitnessFunction'] = swarm.getFitnessObject().getName()
            out['velocityLength'] = math.sqrt(particle.getSqrVelocityVectorLength())
            for key, value in particle.getState().items():
                out['state.' + key] = float(value)
            for key, value in particle.getVelocity().items():
                out['velocity.' + key] = float(value)
            requestPayLoad += json.dumps({'index': {}}) + "\n"
            requestPayLoad += json.dumps(out) + "\n"

        if requestPayLoad != "":
            r = requests.post(self.__bulkUrl, headers={'Content-Type': 'application/json'}, data=requestPayLoad)
