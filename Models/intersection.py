import simpy
class Intersection:
    def __init__(self, env):
        self.env = env
        
        self.traffic_lights = {
            'N' : simpy.PreemptiveResource(env, capacity=1),
            'S' : simpy.PreemptiveResource(env, capacity=1),
            'E' : simpy.PreemptiveResource(env, capacity=1),
            'W' : simpy.PreemptiveResource(env, capacity=1)
        }

        #round robin queues for each direction
        self.queues = {
            'N': [],
            'S': [],
            'E': [],
            'W': []
        }
        self.time_quantum = 10

        self.scheduler_process = env.process(self.scheduler())

        def request_crossing(self, vehicle):
            self.queues[vehicle.source].append(vehicle)
