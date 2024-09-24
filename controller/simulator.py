import random
import time

from controller.config import Config
from model.alien import Alien
from model.location import Location
from model.mars import Mars
from model.rock import Rock
from model.rover import Rover
from model.spacecraft import Spacecraft
from view.gui import Gui


class Simulator:
    """Class representing a simulator."""

    def __init__(self) -> None:
        """
        Initialise the Simulator object.

        Initialises the simulation step, the Mars environment, and generates the initial population of agents.
        """
        self.__simulation_step = 0
        self.__mars = Mars()
        self.__agents = []
        self.__generate_initial_population()
        self.__is_running = False

        agent_colours = {Spacecraft: "red", Rover: "blue", Alien: "green", Rock: "black", None: "white"}
        self.__gui = Gui(self.__mars, agent_colours)
        self.__gui.render()

    def __generate_initial_population(self) -> None:
        """
        Generate the initial population of agents on Mars.

        Adds a spacecraft in the center, rovers next to the spacecraft, and random aliens and rocks across the grid.
        """
        centre_x = self.__mars.get_width() // 2
        centre_y = self.__mars.get_height() // 2
        spacecraft_location = Location(centre_x, centre_y)
        spacecraft = Spacecraft(spacecraft_location)
        self.__mars.set_agent(spacecraft, spacecraft_location)
        self.__agents.append(spacecraft)

        # Generate rovers adjacent to spacecraft
        for _ in range(Config.initial_num_rovers):
            free_locations = self.__mars.get_free_adjacent_locations(spacecraft_location)
            if len(free_locations) > 0:
                rover_location = random.choice(free_locations)
                rover = Rover(rover_location, spacecraft_location)
                self.__mars.set_agent(rover, rover_location)
                self.__agents.append(rover)

        # Generate random aliens and rocks
        for y in range(self.__mars.get_height()):
            for x in range(self.__mars.get_width()):
                location = Location(x, y)

                if self.__mars.get_agent(location) is None:

                    probability = random.random()

                    if probability < Config.alien_creation_probability:
                        alien = Alien(location, spacecraft_location)
                        self.__mars.set_agent(alien, location)
                        self.__agents.append(alien)

                    elif probability < Config.rock_creation_probability:
                        rock = Rock(location)
                        self.__mars.set_agent(rock, location)
                        self.__agents.append(rock)

    def run(self) -> None:
        """Run the simulation."""
        self.__is_running = True

        while self.__is_running:
            self.__update()
            self.__render()
            print("-------------------------------------------------------------------")

            time.sleep(0.01)
            if self.__gui.is_closed():
                self.__is_running = False

    def __render(self) -> None:
        """Render the current state of the simulation."""
        self.__gui.render()

    def __update(self) -> None:
        """Update the simulation state."""
        for agent in self.__agents:
            agent.act(self.__mars)


if __name__ == "__main__":
    """
    Entry point for running the simulation.
    """
    simulation = Simulator()
    simulation.run()
