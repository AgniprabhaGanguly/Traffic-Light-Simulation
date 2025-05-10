import simpy
from Models.intersection import Intersection
from Models.vehicles import Vehicle


def main():
    # Create simulation environment
    env = simpy.Environment()

    # Create intersection
    intersection = Intersection(env)

    # Start vehicle generator process
    #env.process(vehicle_generator(env, intersection, rate=0.2))

    # Create 6 vehicles with different arrival times, sources, destinations and priorities
    vehicles = [
        # Vehicle 1: Arrives at time 0 from North to South
        Vehicle(env=env, id=1, at=0, source='N', destination='S',
                intersection=intersection, prio=0),

        # Vehicle 2: Arrives at time 2 from East to West
        Vehicle(env=env, id=2, at=0, source='E', destination='W',
                intersection=intersection, prio=0),

        # Vehicle 3: Arrives at time 3 from South to East
        Vehicle(env=env, id=3, at=1, source='S', destination='E',
                intersection=intersection, prio=0),

        # Vehicle 4: Arrives at time 5 from West to North
        Vehicle(env=env, id=4, at=2, source='W', destination='N',
                intersection=intersection, prio=1),

        # Vehicle 5: Arrives at time 8 from North to West
        Vehicle(env=env, id=5, at=4, source='N', destination='W',
                intersection=intersection, prio=1),

        # Vehicle 6: Arrives at time 15 from East to South
        Vehicle(env=env, id=6, at=5, source='E', destination='S',
                intersection=intersection, prio=0)
    ]

    # Run simulation
    print("Starting traffic simulation")
    intersection.run(duration=20)

    # Print final statistics
    print("\n=== Final Statistics ===")
    print(f"Simulation ended at time: {env.now:.1f}")

if __name__ == "__main__":
    main()
