import simpy

class Intersection:
    def __init__(self, env):
        self.env = env

        self.traffic_lights = {
            'N' : simpy.Resource(env, capacity=1),
            'S' : simpy.Resource(env, capacity=1),
            'E' : simpy.Resource(env, capacity=1),
            'W' : simpy.Resource(env, capacity=1)
        }

        #round-robin queues for each direction
        self.queues = {
            'N': [],
            'S': [],
            'E': [],
            'W': []
        }
        self.time_quantum = 10

        # Start with all lights red (locked)
        self.red_lights = {}
        for direction in ['N', 'S', 'E', 'W']:
            self.red_lights[direction] = self.traffic_lights[direction].request()

        self.scheduler_process = env.process(self.scheduler())

    def request_crossing(self, vehicle):
        #Add vehicle to queue and return resource request
        self.queues[vehicle.source].append(vehicle)
        request = self.traffic_lights[vehicle.source].request()
        return request

    def remove_from_queue(self, vehicle):
        #Remove vehicle from queue when it has completed crossing
        if vehicle in self.queues[vehicle.source]:
            self.queues[vehicle.source].remove(vehicle)
            print(f"Time {self.env.now:.1f}: Vehicle {vehicle.id} removed from {vehicle.source} queue")

    #controls traffic lights red and green
    def scheduler(self):
        directions = ['N', 'S', 'E', 'W']
        current_direction_index = 0

        while True:
            # check if any vehicle is waiting in the current direction
            current_direction = directions[current_direction_index]

            if not self.queues[current_direction]:
                # if no vehicle is waiting, move to the next direction
                current_direction_index = (current_direction_index + 1) % 4
                yield self.env.timeout(1)
                continue

            # turn current direction green
            self.traffic_lights[current_direction].release(self.red_lights[current_direction])
            print(f'Time {self.env.now:.1f}: Direction : {current_direction} turns green')

            time = 1

            while(time <= self.time_quantum):
                #run for 1 unit of time
                yield self.env.timeout(1)
                time += 1

                # Skip if no vehicle is waiting
                if not self.queues[current_direction]:
                    break

                #check for priority preemption

                #check current direction priority
                current_prio = 0
                for vehicle in self.queues[current_direction]:
                    current_prio += vehicle.prio

                priority_dir_index = self.check_prio_queue(current_prio,  current_direction)

                if priority_dir_index is not None:
                    #set current light to red
                    self.red_lights[current_direction] = self.traffic_lights[current_direction].request()
                    yield self.red_lights[current_direction]
                    print(f'Time {self.env.now:.1f}: Direction : {current_direction} turns red')

                    current_direction_index = priority_dir_index
                    break

            #turn current direction red
            if current_direction not in self.red_lights:
                self.red_lights[current_direction] = self.traffic_lights[current_direction].request()
                yield self.red_lights[current_direction]
                print(f'Time {self.env.now:.1f}: Direction : {current_direction} turns red')

            # rotate to next signal
            if priority_dir_index is None:
                current_direction_index = (current_direction_index + 1) % 4

    def check_prio_queue(self, max_prio, current_direction):
        directions = ['N', 'S', 'E', 'W']
        max_dir_index = None

        for i, direction in enumerate(directions):
            if direction == current_direction:
                continue
            if not self.queues[direction]:
                continue

            p = 0
            for vehicle in self.queues[direction]:
                p += vehicle.prio
            if p > max_prio:
                max_prio = p
                max_dir_index = i

        if max_dir_index is not None:
            dir_name = directions[max_dir_index]
            print(f'Time {self.env.now:.1f}: Priority detected in direction {dir_name} with value {max_prio}')
        return max_dir_index

    def run(self, duration=100):
        print(f"Running simulation for {duration} time units")
        return self.env.run(until=duration)

