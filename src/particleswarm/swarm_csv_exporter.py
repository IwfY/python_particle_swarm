import math

class SwarmCsvExporter(object):
    def __init__(self, filename='swarm_run.csv'):
        self.__filename = filename
        self.__headerWasWritten = False

    def writeHeader(self, swarm):
        with open(self.__filename, 'w') as f:
            particle = swarm.getParticles()[0]
            line = ""
            line += "id,iteration,particle_id,fitness,velocity_length,is_historic_best,is_current_best,"
            state = particle.getState()
            for key in state:
                line += "state.{},velocity.{},".format(key, key)
            f.write(line + '\n')

    def writeParticles(self, swarm, turn):
        if self.__headerWasWritten == False:
            self.writeHeader(swarm)
            self.__headerWasWritten = True

        currentBestPartice = swarm.getCurrentBestParticle()
        historicBestFitness = swarm.getBestFitness()

        with open(self.__filename, 'a') as f:
            for particle in swarm.getParticles():
                line = ""
                line += "{},{},{},{},{},".format(
                    turn * (len(swarm.getParticles()) + 1)  + particle.getId(),
                    turn, particle.getId(),
                    particle.fitness(),
                    math.sqrt(particle.getSqrVelocityVectorLength()))
                line += "{},{},".format(int(particle.fitness() == historicBestFitness), int(particle == currentBestPartice))
                state = particle.getState()
                velocity = particle.getVelocity()
                for key in state:
                    line += "{},{},".format(state[key], velocity[key])
                f.write(line + '\n')
