import simpy
import sys
import time
from visualization.visual_components import TrafficVisualizer

class VisualAdapter:
    def __init__(self, intersection, env):
        self.visualizer = TrafficVisualizer()
        self.intersection = intersection
        self.env = env

        # Initialize the visualizer with our light states
        self.visualizer.light_states = {'N': 'red', 'S': 'red', 'E': 'red', 'W': 'red'}

        # Hook into intersection methods to track light state changes
        self._patch_intersection()

    def _patch_intersection(self):
        def wrapped_scheduler():
            print("==== Wrapped scheduler started! ====")
            directions = ['N', 'S', 'E', 'W']
            current_direction_index = 0

            while True:
                current_direction = directions[current_direction_index]

                # Check if there are vehicles in the current direction
                if not self.intersection.queues[current_direction]:
                    # No vehicles in this direction, move to the next one
                    current_direction_index = (current_direction_index + 1) % 4
                    yield self.env.timeout(1)  # Small delay to avoid tight loop
                    continue

                # Turn the current direction green
                self.intersection.traffic_lights[current_direction].release(
                    self.intersection.red_lights[current_direction])
                self.visualizer.light_states[current_direction] = 'green'
                print(
                    f"DEBUG - Loop start: Time {self.env.now:.1f}, current_direction={current_direction}, Light states: {self.visualizer.light_states}")
                self._update_visualization()

                # Process the green light for the time quantum or until the queue is empty
                time_count = 1
                while time_count <= self.intersection.time_quantum:
                    yield self.env.timeout(1)
                    self._update_visualization()
                    time_count += 1

                    # Check if the queue is empty
                    if not self.intersection.queues[current_direction]:
                        break

                    # Check for priority in other directions
                    current_prio = sum(vehicle.prio for vehicle in self.intersection.queues[current_direction])
                    priority_dir_index = self.intersection.check_prio_queue(current_prio, current_direction)

                    if priority_dir_index is not None:
                        # Priority detected, switch to that direction
                        break

                # Turn the current direction red
                if current_direction not in self.intersection.red_lights:
                    self.intersection.red_lights[current_direction] = self.intersection.traffic_lights[
                        current_direction].request()
                    yield self.intersection.red_lights[current_direction]
                self.visualizer.light_states[current_direction] = 'red'
                self._update_visualization()

                # Update the direction index
                if priority_dir_index is not None:
                    current_direction_index = priority_dir_index
                else:
                    current_direction_index = (current_direction_index + 1) % 4

        self.intersection.scheduler = wrapped_scheduler
        self.intersection.scheduler_process = self.env.process(wrapped_scheduler())

    def _update_visualization(self):
        self.visualizer.vehicle_queues = self.intersection.queues.copy()
        self.visualizer.simulation_time = self.env.now
        self.visualizer.render(self.env.now)

    def run_visual_simulation(self, duration=100):
        print(f"Running visual simulation for {duration} time units")
        self.env.run(until=duration)
        print(f"Visual simulation ended at time {self.env.now:.1f}")

    # def start_rendering_loop(self, fps=5):
    #     def rendering():
    #         while self.visualizer.running:
    #             self._update_visualization()
    #             self.visualizer.render(self.env.now)
    #             yield self.env.timeout(1 / fps)
    #
    #     self.env.process(rendering())

    #
    def run_visual_simulation(self, duration=100, fps=5):
        print(f"Running visual simulation for {duration} time units")
        # Start simulation in step mode
        step_delay = 1 / fps  # Time between steps

        # Run simulation steps
        while self.env.now < duration and self.visualizer.running:
            running, paused = self.visualizer.process_events()

            if not running:
                break

            if not paused:
                try:
                    self.env.step()
                    self._update_visualization()
                    self.visualizer.render(self.env.now)
                except StopIteration:
                    break
            else:
                # Just update the visualization when paused
                self.visualizer.render()

            time.sleep(step_delay)  # Control simulation speed

        print(f"Visual simulation ended at time {self.env.now:.1f}")