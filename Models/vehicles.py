class Vehicle:
    def init(self, id, at, source, destination, prio=0):
        #source and destination to be passed at N, S, E, W

        self.id = id
        self.at = at    #arrival time
        self.source = source  # source lane (kahan se gaddi aa rhi h)
        self.destination = destination  # destination lane (kahan pe gaddi jana chahti h)
        self.prio = prio # higher number = higher priority

        # all vehicles take 2 unit time to cross the intersection and reach its dest.
        self.crossing_time = 2 # time taken to cross the intersection

        #state of the vehicle
        self.wt = 0
        self.status = "waiting" # waiting, crossing, done

    def wait(self):
        self.wt += 1

    def start_crossing(self):
        self.status = "crossing"

        #crossing time simulate?

    def ct(self):
        return self.at + self.wt + self.crossing_time;

    def __str__(self):
        """String representation of the vehicle for debugging and display."""
        return f"Vehicle {self.id}: {self.source}->{self.destination} Status {self.status}, Arrival Time {self.at}, Wait Time {self.wt}, Priority {self.prio}"
