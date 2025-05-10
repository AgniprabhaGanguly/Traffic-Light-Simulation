class Vehicle:

    def __init__(self, env, id, at, source, destination, intersection, prio=0):
        #source and destination to be passed at N, S, E, W

        self.env = env
        self.id = id
        self.arrival_time = at
        self.source = source  # source lane (kahan se gaddi aa rhi h)
        self.destination = destination  # destination lane (kahan pe gaddi jana chahti h)
        self.intersection = intersection # intersection is a resource
        self.prio = prio # higher number = higher priority
        self.crossing_time = 1 # time taken to cross the intersection

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

        print(self)
        self.wait_start_time = self.env.now

        with self.intersection.request_crossing(self) as request:
            yield request

            self.wait_end_time = self.env.now
            self.wt = self.wait_end_time - self.wait_start_time

            self.status = "crossing"
            print(
                f"Time {self.env.now:.1f}: Vehicle {self.id} starts crossing from {self.source} to {self.destination}")

            # Cross the intersection
            yield self.env.timeout(self.crossing_time)

            # Completed crossing
            self.status = "done"
            self.intersection.remove_from_queue(self)
            print(f"Time {self.env.now:.1f}: Vehicle {self.id} completed crossing")

    def __str__(self):
        """String representation of the vehicle for debugging and display."""
        return f"Vehicle {self.id}: {self.source}->{self.destination} Status {self.status}, Arrival Time {self.arrival_time}, Wait Time {self.wt}, Priority {self.prio}"
