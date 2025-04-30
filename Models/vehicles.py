import simpy

class Vehicle:

    def init(self, env, id, at, source, destination, intersection, prio=0):
        #source and destination to be passed at N, S, E, W

        self.env = env
        self.id = id
        self.arrival_time = at
        self.source = source  # source lane (kahan se gaddi aa rhi h)
        self.destination = destination  # destination lane (kahan pe gaddi jana chahti h)
        self.intersection = intersection # intersection is a resource
        self.prio = prio # higher number = higher priority
        self.crossing_time = 2 # time taken to cross the intersection

        # Timing statistics
        self.wait_start_time = None
        self.wait_end_time = None

        #state of the vehicle
        self.wt = 0
        self.status = "waiting" # waiting, crossing, done

        self.process = env.process(self.run())

    def run(self):
        if self.env.now < self.arrival_time:
                yield self.env.timeout(self.arrival_time - self.env.now)
        print(f"Vehicle {self.id} arrived at time : {self.env.now} going from {self.source} to {self.destination}")

    def __str__(self):
        """String representation of the vehicle for debugging and display."""
        return f"Vehicle {self.id}: {self.source}->{self.destination} Status {self.status}, Arrival Time {self.arrival_time}, Wait Time {self.wt}, Priority {self.prio}"
