import simpy
import sys
import time
from visualization.visual_components import TrafficVisualizer


class VisualAdapter:
    def __init__(self, intersection, env):
        self.visualizer = TrafficVisualizer()
        self.intersection = intersection
        self.env = env
        self.light_states = {'N': 'red', 'S': 'red', 'E': 'red', 'W': 'red'}

        # Hook into intersection methods to track light state changes
        self._patch_intersection()

    def _patch_intersection(self):
        """Monkey patch the intersection to track light changes"""
        original_scheduler = self.intersection.scheduler

        def wrapped_scheduler():
            directions = ['N', 'S', 'E', 'W']
            current_direction_index = 0

            while True:
                # Update visualization before making decisions
                self._update_visualization()

                current_direction = directions[current_direction_index]

                if not self.intersection.queues[current_direction]:
                    current_direction_index = (current_direction_index + 1) % 4
                    yield self.env.timeout(1)
                    continue

                # Turn current direction green
                self.intersection.traffic_lights[current_direction].release(
                    self.intersection.red_lights[current_direction])
                self.light_states[current_direction] = 'green'  # Track light state
                print(f'Time {self.env.now:.1f}: Direction : {current_direction} turns green')

                time_count = 1
                while time_count <= self.intersection.time_quantum:
                    yield self.env.timeout(1)
                    self._update_visualization()  # Update after each time step
                    time_count += 1

                    if not self.intersection.queues[current_direction]:
                        break

                    current_prio = sum(vehicle.prio for vehicle in self.intersection.queues[current_direction])
                    priority_dir_index = self.intersection.check_prio_queue(current_prio, current_direction)

                    if priority_dir_index is not None:
                        self.intersection.red_lights[current_direction] = self.intersection.traffic_lights[
                            current_direction].request()
                        yield self.intersection.red_lights[current_direction]
                        self.light_states[current_direction] = 'red'  # Track light state
                        print(f'Time {self.env.now:.1f}: Direction : {current_direction} turns red')

                        current_direction_index = priority_dir_index
                        break

                if current_direction not in self.intersection.red_lights:
                    self.intersection.red_lights[current_direction] = self.intersection.traffic_lights[
                        current_direction].request()
                    yield self.intersection.red_lights[current_direction]
                    self.light_states[current_direction] = 'red'  # Track light state
                    print(f'Time {self.env.now:.1f}: Direction : {current_direction} turns red')

                if priority_dir_index is None:
                    current_direction_index = (current_direction_index + 1) % 4

        self.intersection.scheduler = wrapped_scheduler

    def _update_visualization(self):
        """Update the visualization state"""
        self.visualizer.light_states = self.light_states.copy()
        self.visualizer.vehicle_queues = self.intersection.queues.copy()
        self.visualizer.simulation_time = self.env.now

    def run_visual_simulation(self, duration=100, fps=5):
        """Run the simulation with visualization"""
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