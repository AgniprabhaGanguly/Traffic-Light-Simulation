import simpy
from Models.intersection import Intersection
from Models.vehicles import Vehicle
from visualization.visual_simulation import VisualAdapter
import random

def setup_vehicle_generator(env, intersection):
    """
    Sets up a continuous vehicle generator process that creates vehicles
    with random properties at random intervals throughout the simulation.

    Args:
        env: SimPy environment
        intersection: Intersection instance
    """
    def vehicle_generator():
        vehicle_id = 1

        # Define possible vehicle routes
        directions = ['N', 'S', 'E', 'W']

        while True:
            # Random arrival time interval between 1-5 time units
            arrival_interval = random.uniform(1, 5)
            yield env.timeout(arrival_interval)

            # Generate random vehicle properties
            source = random.choice(directions)

            # Avoid having the destination be the same as the source
            possible_destinations = [d for d in directions if d != source]
            destination = random.choice(possible_destinations)

            # 20% chance of priority vehicle
            priority = 1 if random.random() < 0.2 else 0

            # Create and add the vehicle
            Vehicle(
                env=env,
                id=vehicle_id,
                at=env.now,
                source=source,
                destination=destination,
                intersection=intersection,
                prio=priority
            )

            print(f"Vehicle {vehicle_id}: {source}->{destination} Status waiting, "
                  f"Arrival Time {env.now}, Wait Time 0, Priority {priority}")

            vehicle_id += 1

    # Start the generator process
    return env.process(vehicle_generator())

def main():
    # Create simulation environment
    env = simpy.Environment()

    # Create intersection
    intersection = Intersection(env)

    # Create visualization adapter
    visual_adapter = VisualAdapter(intersection, env)

    # Create vehicles
    vehicles = [
        # Vehicle 1: Arrives at time 0 from North to South
        Vehicle(env=env, id=1, at=0, source='N', destination='S',
                intersection=intersection, prio=0),

        # Vehicle 2: Arrives at time 0 from East to West
        Vehicle(env=env, id=2, at=0, source='E', destination='W',
                intersection=intersection, prio=0),

        # Vehicle 3: Arrives at time 1 from South to East
        Vehicle(env=env, id=3, at=1, source='S', destination='E',
                intersection=intersection, prio=0),

        # Vehicle 4: Arrives at time 2 from West to North
        Vehicle(env=env, id=4, at=2, source='W', destination='N',
                intersection=intersection, prio=1),

        # Vehicle 5: Arrives at time 4 from North to West
        Vehicle(env=env, id=5, at=4, source='N', destination='W',
                intersection=intersection, prio=1),

        # Vehicle 6: Arrives at time 5 from East to South
        Vehicle(env=env, id=6, at=5, source='E', destination='S',
                intersection=intersection, prio=0)
    ]

    #vehicle_gen_process = setup_vehicle_generator(env, intersection)

    # Run visual simulation
    print("Starting visual traffic simulation")
    # visual_adapter.start_rendering_loop(fps=5)

    visual_adapter.run_visual_simulation(duration=20)

    # Print final statistics
    print("\n=== Final Statistics ===")
    print(f"Simulation ended at time: {env.now:.1f}")

if __name__ == "__main__":
    main()