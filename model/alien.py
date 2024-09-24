from __future__ import annotations

from typing import TYPE_CHECKING
import random

from model.rover import Rover
from model.agent import Agent
from model.location import Location
from model.spacecraft import Spacecraft

if TYPE_CHECKING:
    from model.mars import Mars


class Alien(Agent):
    __alien_count = 1
    DEFAULT_ENERGY_LIFE = 100
    MAX_CHASE_MOVES = 3

    def __init__(
            self,
            location: Location,
            space_craft_location: Location,
            energy_life: int = DEFAULT_ENERGY_LIFE
    ):
        super().__init__(location)
        self.energy = energy_life
        self.id = Alien.__alien_count
        Alien.__alien_count += 1
        self.hibernating = False
        self.__space_craft_location = space_craft_location
        self.is_chasing_rover = False
        self.chase_moves = 0
        self.chasing_rover = None

    def __move(self, mars: Mars, new_location: Location):
        """
        Move the alien to a new location.

        Args:
            mars (Mars): The Mars environment.
            new_location (Location): The new location to move the alien to.
        """
        previous_location = self.get_location()
        mars.set_agent(self, new_location)
        self.set_location(new_location)
        mars.set_agent(None, previous_location)
        print(f"Alien {self.id} moved from {previous_location} to {new_location} with energy {self.energy}%.")
        self.energy -= 5
        if self.energy <= 0:
            self.energy = 0

    def __random_move(self, mars: Mars) -> None:
        """
        Moves the alien randomly to an adjacent free location on the grid.
        """
        if self.hibernating:
            print(f"Alien {self.id} is hibernating and cannot move randomly.")
            return

        free_locations = mars.get_free_adjacent_locations(self.get_location())
        if free_locations:
            random_free_location = random.choice(free_locations)
            self.__move(mars, random_free_location)
            self.energy -= 5
            if self.energy <= 0:
                self.energy = 0
            print(f"Alien {self.id} moved randomly to {random_free_location} with energy {self.energy}%.")

    def __detect_rovers(self, mars: Mars) -> None:
        """
        Detects rovers and chases the nearest one.
        """
        if self.hibernating:
            print(f"Alien {self.id} is hibernating and cannot detect or chase rovers.")
            return
        if not self.is_chasing_rover:
            adjacent_locations = mars.get_adjacent_locations_upto_3_cells(self.get_location())
            rovers_in_range = [mars.get_agent(loc) for loc in adjacent_locations if
                               isinstance(mars.get_agent(loc), Rover)]
            if rovers_in_range:
                nearest_rover = min(rovers_in_range,
                                    key=lambda rover: self.__calculate_distance(rover.get_location(),
                                                                                  self.get_location()))
                print(f"Alien {self.id} detected rover at {nearest_rover.get_location()} and is chasing it.")
                self.is_chasing_rover = True
                self.chasing_rover = nearest_rover

    def __chase_rover(self, mars: Mars, rover: Rover) -> None:
        """
        Moves the alien towards the nearest rover and attacks if within reach.
        """
        if self.hibernating:
            print(f"Alien {self.id} is hibernating and cannot chase rovers.")
            return
        self.chase_moves += 1
        rover_location = rover.get_location()
        self_location = self.get_location()
        if self.__calculate_distance(rover_location, self_location) == 1:
            print(f"Alien {self.id} is attacking rover at {rover_location}.")
            self.__attack_rover(rover)
        else:
            new_location = self.__move_towards_adjacent(rover_location, self_location, mars)
            if new_location:
                self.__move(mars, new_location)
                if rover.damaged:
                    rover.set_location(new_location)
                print(f"Alien {self.id} chased rover to {new_location} with energy {self.energy}%.")

    def __attack_rover(self, rover: Rover) -> None:
        """
        Attacks the rover, causing it to sustain damage and reducing the alien's energy.
        """

        if self.hibernating:
            print(f"Alien {self.id} is hibernating and cannot attack rovers.")
            return
        if self.energy <= 20:
            self.hibernating = True
            print(f"Alien {self.id}'s energy is too low. Alien is now hibernating.")
        if not rover.damaged:
            rover.sustain_damage(25)
            self.energy -= 20
            if self.energy <= 0:
                self.energy = 0
            print(f"Alien {self.id} attacked rover. Alien's energy is now {self.energy}%.")

    def __hibernate(self) -> None:
        """
        Gradually restores the alien's energy when hibernating.
        """
        if self.hibernating:
            self.energy += 10
            print(f"Alien {self.id} is hibernating. Energy restored to {self.energy}%.")

            if self.energy >= 100:
                self.energy = 100
                self.hibernating = False
                print(f"Alien {self.id}'s energy is fully restored. Alien is no longer hibernating.")

    def __move_to_location(self, target_location: Location, mars: Mars) -> None:
        """
        Move the alien towards the specified target location.

        Args:
            target_location (Location): The target location to move towards.
            mars (Mars): The Mars environment.
        """
        current_location = self.get_location()
        dx = target_location.get_x() - current_location.get_x()
        dy = target_location.get_y() - current_location.get_y()

        # Determine the direction of movement
        dir_x = 1 if dx > 0 else -1 if dx < 0 else 0
        dir_y = 1 if dy > 0 else -1 if dy < 0 else 0

        # Calculate the new location
        new_x = current_location.get_x() + dir_x
        new_y = current_location.get_y() + dir_y
        new_location = Location(new_x, new_y)

        # Check if the new location is valid and move if possible
        if new_location in mars.get_free_adjacent_locations(current_location):
            self.__move(mars, new_location)
        else:
            # If the new location is not valid or occupied, move randomly
            self.__random_move(mars)

    def __avoid_spacecraft(self, mars: Mars) -> None:
        """
        Moves the alien away from the spacecraft if it gets too close.
        """
        if self.hibernating:
            print(f"Alien {self.id} is hibernating and cannot avoid the spacecraft.")
            return

        current_location = self.get_location()
        spacecraft_location = self.__space_craft_location

        # Move to a location farther away from the spacecraft
        farthest_location = None
        max_distance = 0
        for loc in mars.get_free_adjacent_locations(current_location):
            distance = self.__calculate_distance(loc, spacecraft_location)
            if distance > max_distance:
                max_distance = distance
                farthest_location = loc

        if farthest_location:
            self.__move_to_location(farthest_location, mars)
            print(f"Alien {self.id} avoid spacecraft to {farthest_location} with energy {self.energy}%.")
        else:
            print(f"Alien {self.id} could not find a safe location to move away from the spacecraft.")

    @staticmethod
    def __calculate_distance(location1: Location, location2: Location) -> int:
        return abs(location1.get_x() - location2.get_x()) + abs(location1.get_y() - location2.get_y())

    @staticmethod
    def __move_towards_adjacent(target_location: Location, current_location: Location, mars: Mars) -> Location | None:
        x1, y1 = current_location.get_x(), current_location.get_y()
        x2, y2 = target_location.get_x(), target_location.get_y()

        # Determine the direction to move
        new_x = x1 + (1 if x2 > x1 else -1 if x2 < x1 else 0)
        new_y = y1 + (1 if y2 > y1 else -1 if y2 < y1 else 0)

        possible_new_location = Location(new_x, new_y)
        if mars.get_free_adjacent_locations(possible_new_location) and possible_new_location != target_location:
            return possible_new_location

    def act(self, mars: Mars) -> None:
        """
        Defines the alien's actions on each turn.
        """
        current_location = self.get_location()

        spacecraft_distance = self.__calculate_distance(self.__space_craft_location, current_location)
        if spacecraft_distance <= 4:
            self.__avoid_spacecraft(mars)
            return

        if self.hibernating:
            self.__hibernate()
            return

        adjacent_locations = mars.get_adjacent_locations_upto_3_cells(current_location)
        found_rovers = [mars.get_agent(loc) for loc in adjacent_locations if isinstance(mars.get_agent(loc), Rover)]

        if found_rovers:
            rover = random.choice(found_rovers)
            if not rover.damaged:
                self.__chase_rover(mars, rover)
                if self.chase_moves >= self.MAX_CHASE_MOVES:
                    self.is_chasing_rover = False
                    self.chase_moves = 0
                return

        self.__random_move(mars)
