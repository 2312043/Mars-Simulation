class Config:
    """Class representing configuration parameters for a simulation."""

    simulation_name = "Mars Simulation"
    min_simulation_speed = 0
    max_simulation_speed = 100
    initial_simulation_speed = (max_simulation_speed - min_simulation_speed) // 2
    world_size = 20

    alien_creation_probability = 0.01
    rock_creation_probability = 0.8

    initial_num_rovers = 8
