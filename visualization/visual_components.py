import pygame
import sys

class TrafficVisualizer:
    def __init__(self, width=800, height=800):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Traffic Simulation")
        self.clock = pygame.time.Clock()

        # Colors
        self.black = (0, 0, 0)
        self.white = (255, 255, 255)
        self.gray = (100, 100, 100)
        self.red = (255, 0, 0)
        self.green = (0, 255, 0)
        self.blue = (0, 0, 255)
        self.orange = (255, 165, 0)
        self.purple = (128, 0, 128)
        self.background_green = (100, 200, 100)

        # Font
        self.font = pygame.font.SysFont('Arial', 16)

        # Simulation time and states
        self.simulation_time = 0
        self.light_states = {'N': 'red', 'S': 'red', 'E': 'red', 'W': 'red'}
        self.vehicle_queues = {'N': [], 'S': [], 'E': [], 'W': []}

        # Simulation control
        self.running = True
        self.paused = False

        # Load car images
        self.car_normal = pygame.image.load('assets/car_normal.png').convert_alpha()
        self.car_priority = pygame.image.load('assets/car_priority.png').convert_alpha()

        # Get original dimensions
        original_width = self.car_normal.get_width()
        original_height = self.car_normal.get_height()

        target_width = 80

        # Calculate height that maintains aspect ratio
        aspect_ratio = original_height / original_width
        target_height = int(target_width * aspect_ratio)

        # Scale images while maintaining aspect ratio
        self.car_normal = pygame.transform.smoothscale(self.car_normal, (target_width, target_height))
        self.car_priority = pygame.transform.smoothscale(self.car_priority, (target_width, target_height))

    def process_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused

        return self.running, self.paused

    def draw_background(self):
        """Draw the background and roads"""
        self.screen.fill(self.background_green)

        # Draw roads
        road_width = 100
        # North-South road
        pygame.draw.rect(self.screen, self.gray, (self.width/2 - road_width/2, 0, road_width, self.height))
        # East-West road
        pygame.draw.rect(self.screen, self.gray, (0, self.height/2 - road_width/2, self.width, road_width))

        # Draw lane markings
        lane_marking_length = 40
        lane_marking_width = 8
        lane_gap = 30

        # North-South lane markings
        for y in range(0, self.height, lane_gap):
            if not (self.height/2 - road_width < y < self.height/2 + road_width):  # Skip intersection
                pygame.draw.rect(self.screen, self.white,
                                (self.width/2 - lane_marking_width/2, y, lane_marking_width, lane_marking_length))

        # East-West lane markings
        for x in range(0, self.width, lane_gap):
            if not (self.width/2 - road_width < x < self.width/2 + road_width):  # Skip intersection
                pygame.draw.rect(self.screen, self.white,
                                (x, self.height/2 - lane_marking_width/2, lane_marking_length, lane_marking_width))

    def draw_traffic_lights(self):
                """Draw the traffic lights as flat boxes across the roads"""
                light_box_width = 80  # Now wider, oriented parallel to the road
                light_box_height = 30  # Now shorter
                light_radius = 10

                light_positions = {
                    'N': (self.width/2 + 60, self.height/2 - 70),  # North
                    'S': (self.width/2 - 60, self.height/2 + 70),  # South
                    'E': (self.width/2 + 70, self.height/2 + 60),  # East
                    'W': (self.width/2 - 70, self.height/2 - 60),  # West
                }

                for direction, position in light_positions.items():
                    is_vertical = direction in ['N', 'S']

                    if is_vertical:
                        box_rect = pygame.Rect(position[0] - light_box_width/2,
                                            position[1] - light_box_height/2,
                                            light_box_width, light_box_height)
                    # For horizontal roads, make the box horizontal but in the right orientation
                    else:
                        box_rect = pygame.Rect(position[0] - light_box_height/2,
                                            position[1] - light_box_width/2,
                                            light_box_height, light_box_width)

                    pygame.draw.rect(self.screen, self.black, box_rect)
                    pygame.draw.rect(self.screen, (50, 50, 50), box_rect, 2)  # Gray border

                    # Calculate positions for the three lights (red, yellow, green)
                    if is_vertical:
                        red_pos = (position[0] - light_box_width/4, position[1])
                        yellow_pos = (position[0], position[1])
                        green_pos = (position[0] + light_box_width/4, position[1])
                    else:
                        red_pos = (position[0], position[1] - light_box_width/4)
                        yellow_pos = (position[0], position[1])
                        green_pos = (position[0], position[1] + light_box_width/4)

                    # Draw all three lights (dimmed when inactive)
                    pygame.draw.circle(self.screen, (100, 0, 0), red_pos, light_radius)  # Dimmed red
                    pygame.draw.circle(self.screen, (100, 100, 0), yellow_pos, light_radius)  # Dimmed yellow
                    pygame.draw.circle(self.screen, (0, 100, 0), green_pos, light_radius)  # Dimmed green

                    #Active light
                    if self.light_states[direction] == 'green':
                        pygame.draw.circle(self.screen, self.green, green_pos, light_radius)
                    elif self.light_states[direction] == 'red':
                        pygame.draw.circle(self.screen, self.red, red_pos, light_radius)

                    # Add direction label
                    text = self.font.render(direction, True, self.white)
                    if is_vertical:
                        text_rect = text.get_rect(center=(position[0], position[1] - light_box_height/2 - 15))
                    else:
                        text_rect = text.get_rect(center=(position[0] - light_box_height/2 - 15, position[1]))
                    self.screen.blit(text, text_rect)

    def draw_vehicles(self):
        """Draw vehicles in each queue as PNG sprites"""
        road_width = 100  # Match your road width from draw_background
        lane_offset = road_width / 4  # Half of half the road width to position in the correct lane

        # Adjust vehicle spacing - increase or decrease these values to change spacing
        vehicle_spacing = 80

        bold_font = pygame.font.SysFont('Arial', 18, bold=True)

        queue_positions = {
            'N': {'x': self.width / 2 + lane_offset, 'y': self.height / 2 - 150, 'dx': 0, 'dy': -vehicle_spacing,
                  'angle': 180},
            'S': {'x': self.width / 2 - lane_offset, 'y': self.height / 2 + 150, 'dx': 0, 'dy': vehicle_spacing,
                  'angle': 0},
            'E': {'x': self.width / 2 + 150, 'y': self.height / 2 + lane_offset, 'dx': vehicle_spacing, 'dy': 0,
                  'angle': 90},
            'W': {'x': self.width / 2 - 150, 'y': self.height / 2 - lane_offset, 'dx': -vehicle_spacing, 'dy': 0,
                  'angle': 270},
        }

        for direction, vehicles in self.vehicle_queues.items():
            pos = queue_positions[direction]
            for i, vehicle in enumerate(vehicles):
                x = pos['x'] + i * pos['dx']
                y = pos['y'] + i * pos['dy']

                # Select car image based on priority
                car_img = self.car_priority if vehicle.prio > 0 else self.car_normal

                # Just rotate without any extra scaling
                rotated_car = pygame.transform.rotate(car_img, pos['angle'])

                # Get rect for centered positioning
                car_rect = rotated_car.get_rect(center=(x, y))

                # Draw the car
                self.screen.blit(rotated_car, car_rect)

                # Draw vehicle ID and destination
                text = bold_font.render(f"{vehicle.id} : {vehicle.source}->{vehicle.destination}", True, self.black)
                text_rect = text.get_rect(center=(x, y - 45))  # Position text above car
                self.screen.blit(text, text_rect)

    def draw_simulation_info(self):
        """Draw simulation information"""
        info_text = f"Simulation Time: {self.simulation_time:.1f}"
        text_surface = self.font.render(info_text, True, self.black)
        self.screen.blit(text_surface, (10, 10))

        if self.paused:
            pause_text = "PAUSED - Press SPACE to continue"
            pause_surface = self.font.render(pause_text, True, self.red)
            self.screen.blit(pause_surface, (10, 40))
        else:
            controls_text = "Press SPACE to pause"
            controls_surface = self.font.render(controls_text, True, self.black)
            self.screen.blit(controls_surface, (10, 40))

    def render(self, simulation_time=None):
        """Render the current state"""
        if simulation_time is not None:
            self.simulation_time = simulation_time

        self.draw_background()
        self.draw_traffic_lights()
        self.draw_vehicles()
        self.draw_simulation_info()

        pygame.display.flip()
        self.clock.tick(30)  # 30 FPS