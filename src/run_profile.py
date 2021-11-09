from particleswarm import *
import profile


class Fitness1(fitness.Fitness):
    def calculateFitness(self, state):
        return abs(pow(state["x"], 3) + 0.5 * state["y"] - 20.5)


def find_solution(swarm, exporter, iterations):
    for i in range(iterations):
        swarm.step()
        exporter.writeParticles(swarm, i + 1)
    print(swarm.getCurrentBestParticle().getState())
    print(swarm.getCurrentBestParticle().getFitness())


if __name__ == '__main__':
    s = swarm.Swarm()
    particleVelocityUpdateStrategy = default_particle_velocity_update_strategy.DefaultParticleVelocityUpdateStrategy(s, 0.6, 0.3, 0.3, 0.3)
    s.setParticleVelcityUpdateStrategyObject(particleVelocityUpdateStrategy)

    exporter = swarm_sqlite_exporter.SwarmSqliteExporter('test.sqlite')

    s.addDimension("x", -10, 10)
    s.addDimension("y", -10, 10)
    s.setFitnessObject(Fitness1())
    s.populate(100)
    profile.run("find_solution(s, exporter, 10)")
