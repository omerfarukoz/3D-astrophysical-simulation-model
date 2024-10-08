from vpython import *
import math
import random

scene = canvas(title="Planet Simulation", width=1000, height=1000, background=color.black)

G = 6.674 * 10**-11
time_step = 3*1e9
scale_factor = 1e-12


camera_pos = vector(0,0,0)
camera_angle = vector(0,0,0)

def key_down(evt):
    global camera_pos, camera_angle
    if evt.key == 'w':  
        camera_pos += vector(0, 0, 0.1)
    elif evt.key == 's':  
        camera_pos += vector(0, 0, -0.1)
    elif evt.key == 'a':  
        camera_pos += vector(-0.1, 0, 0)
    elif evt.key == 'd':  
        camera_pos += vector(0.1, 0, 0)
    elif evt.key == 'e':  
        camera_pos += vector(0, 0.1, 0) 
    elif evt.key == 'q':  
        camera_pos += vector(0, -0.1, 0)
    elif evt.key == 'up':  
        camera_angle.x += 0.1
    elif evt.key == 'down':  
        camera_angle.x -= 0.1
    elif evt.key == 'left':  
        camera_angle.y += 0.1
    elif evt.key == 'right':  
        camera_angle.y -= 0.1
    
    scene.camera.pos = camera_pos
    scene.camera.axis = vector(sin(camera_angle.y), sin(camera_angle.x), cos(camera_angle.y))

#scene.bind('keydown', key_down)

class Planet:
    def __init__(self, name, mass, radius, coordinates, velocity, color):
        self.name = name
        self.mass = mass
        self.radius = radius
        self.coordinates = coordinates
        self.velocity = velocity
        self.color = color
        self.sphere = sphere(pos=vector(coordinates[0] * scale_factor, coordinates[1] * scale_factor, coordinates[2] * scale_factor),
                             radius=radius * 1e-2,
                             color=color)
        self.path = []

    def update_position(self):
        self.coordinates[0] += self.velocity[0] * time_step
        self.coordinates[1] += self.velocity[1] * time_step
        self.coordinates[2] += self.velocity[2] * time_step
        self.sphere.pos = vector(self.coordinates[0] * scale_factor, self.coordinates[1] * scale_factor, self.coordinates[2] * scale_factor)
        self.path.append(vector(self.coordinates[0] * scale_factor, self.coordinates[1] * scale_factor, self.coordinates[2] * scale_factor))
        if len(self.path) > 1:
            curve(pos=self.path, color=self.color)


def create_stars(num_stars):
    for _ in range(num_stars):
        x = random.uniform(-500, 500)
        y = random.uniform(-500, 500)
        z = random.uniform(-500, 500)
        size = random.uniform(0.01, 0.03)
        sphere(pos=vector(x, y, z), radius=size, color=color.white)

def calculate_gravitational_force(planet1, planet2):
    r_vector = vector(planet2.coordinates[0] - planet1.coordinates[0],
                      planet2.coordinates[1] - planet1.coordinates[1],
                      planet2.coordinates[2] - planet1.coordinates[2])
    r = mag(r_vector)
    if r == 0:
        return vector(0, 0, 0)
    force_magnitude = G * planet1.mass * planet2.mass / r**2
    force_direction = norm(r_vector)
    return force_direction * force_magnitude

def check_collision(p1, p2):
    distance = mag(vector(p2.coordinates[0] - p1.coordinates[0],
                          p2.coordinates[1] - p1.coordinates[1],
                          p2.coordinates[2] - p1.coordinates[2]))
    combined_radius = (p1.radius + p2.radius) * 7* 1e9 
    return distance < combined_radius

def merge_planets(p1, p2):
    new_mass = p1.mass + p2.mass
    new_radius = (p1.radius**3 + p2.radius**3)**(1/3)
    new_coordinates = [
        (p1.coordinates[0] * p1.mass + p2.coordinates[0] * p2.mass) / new_mass,
        (p1.coordinates[1] * p1.mass + p2.coordinates[1] * p2.mass) / new_mass,
        (p1.coordinates[2] * p1.mass + p2.coordinates[2] * p2.mass) / new_mass
    ]
    new_velocity = [
        (p1.velocity[0] * p1.mass + p2.velocity[0] * p2.mass) / new_mass,
        (p1.velocity[1] * p1.mass + p2.velocity[1] * p2.mass) / new_mass,
        (p1.velocity[2] * p1.mass + p2.velocity[2] * p2.mass) / new_mass
    ]
    new_color = (p1.color + p2.color) / 2
    p1.sphere.visible = False
    p2.sphere.visible = False

    return Planet(f"Merged Planet ({p1.name} & {p2.name})", new_mass, new_radius, new_coordinates, new_velocity, new_color)

def update_velocities(planets):
    for i, planet1 in enumerate(planets):
        total_force = vector(0, 0, 0)
        for j, planet2 in enumerate(planets):
            if i != j:
                total_force += calculate_gravitational_force(planet1, planet2)
        ax = total_force.x / planet1.mass
        ay = total_force.y / planet1.mass
        az = total_force.z / planet1.mass
        planet1.velocity[0] += ax * time_step
        planet1.velocity[1] += ay * time_step
        planet1.velocity[2] += az * time_step

def update_positions(planets):
    to_remove = []
    for i in range(len(planets)):
        planet1 = planets[i]
        planet1.update_position()
        for j in range(i + 1, len(planets)):
            planet2 = planets[j]
            if check_collision(planet1, planet2):
                new_planet = merge_planets(planet1, planet2)
                planets.append(new_planet)
                to_remove.extend([planet1, planet2])
                break
    for planet in to_remove:
        if planet in planets:
            planets.remove(planet)

def simulate(planets):
    while True:
        rate(10)
        update_velocities(planets)
        update_positions(planets)

planets = [
    Planet("Planet 1", 5.972 * 10**28, 4000, [5.972 * 10**14, 300, 0], [0, 160, 0], color.red),
    Planet("Planet 2", 9.000 * 10**26, 5000, [24 * 10**13, 5.972 * 10**13, 100], [0, 600, -400], color.blue),
    Planet("Planet 3", 7.348 * 10**30, 2000, [23 * 10**13, 5.972 * 10**14, 50], [1000, 0, 500], color.green),
    Planet("Planet 4", 7 * 10**30, 9000, [5.972 * 10**14, 4 * 10**14, -50], [-1000, 0, 300], color.orange),
    Planet("Planet 5", 2 * 10**31, 8000, [5.972 * 10**13, 4 * 10**14, -50], [0, -2500, -400], color.purple),

]
simulate(planets)
