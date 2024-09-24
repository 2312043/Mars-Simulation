from __future__ import annotations

import random
from typing import TYPE_CHECKING, List

from model.rock import Rock
from model.agent import Agent
from model.location import Location

if TYPE_CHECKING:
    from model.mars import Mars


class Rover(Agent):
    """
    Represents a rover agent in the simulation.

    Attributes:
        __space_craft_location: The location of the spacecraft the rover is assigned to.
        __rock: The rock picked up by the rover.
        __remembered_rocks: List of locations of rocks the rover has seen.
        id: The identifier for the rover.
        battery_life: The remaining battery life of the rover.
        battery_consumption_per_move: Battery consumption per move.
    """

    __rover_count = 1
    DEFAULT_BATTERY_LIFE = 100
    DEFAULT_BATTERY_CONSUMPTION_PER_MOVE = 5

    def __init__(
            self,
            location: Location,
            space_craft_location: Location,
            battery_life: int = DEFAULT_BATTERY_LIFE,
            battery_consumption_per_move: int = DEFAULT_BATTERY_CONSUMPTION_PER_MOVE
    ):
        """
        Initialize the Rover object with its location and assigned spacecraft location.

        Args:
            location (Location): The initial location of the rover.
            space_craft_location (Location): The location of the spacecraft the rover is assigned to.
            battery_life (int): The initial battery life of the rover.
            battery_consumption_per_move (int): Battery consumption per move.
        """
        super().__init__(location)
        self.__space_craft_location = space_craft_location
        self.__rock = None
        self.__remembered_rocks = []
        self.id = Rover.__rover_count
        Rover.__rover_count += 1
        self.battery_life = battery_life
        self.battery_consumption_per_move = battery_consumption_per_move
        self.request_charging = False
        self.target_location = None
        self.damaged = False
        self.ignore_battery = False
        self.visited_locations: List[Location] = []

    def __repr__(self) -> str:
        """
        Return a string representation of the Rover object.

        Returns:
            str: A string representation of the Rover object.
        """
        return f"Rover {self.id}({repr(self.get_location())})"

    def __str__(self) -> str:
        """
        Return a string describing the current location of the rover.

        Returns:
            str: A string describing the current location of the rover.
        """
        return f"Rover {self.id} is located at: ({repr(self.get_location())})"

    def __move(self, mars: Mars, new_location: Location):
        """
        Move the rover to a new location and remember any rocks it sees.

        Args:
            mars (Mars): The Mars environment.
            new_location (Location): The new location to move the rover to.
        """
        previous_location = self.get_location()
        mars.set_agent(self, new_location)
        self.set_location(new_location)
        mars.set_agent(None, previous_location)
        if self.__rock:
            self.__rock.set_location(new_location)

        # Remember rocks in adjacent cells
        self.__remember_rocks(mars)

    def __move_to_random_location(self, mars: Mars):
        """
        Move the rover to a random adjacent location on Mars.

        Args:
            mars (Mars): The Mars environment.
        """
        current_location = self.get_location()
        free_locations = mars.get_free_adjacent_locations(current_location)
        next_location = random.choice(free_locations)
        self.__move(mars, next_location)

    def __move_to_explore_location(self, mars: Mars):
        """
        Move the rover to a random adjacent location on Mars, prioritizing unvisited locations.

        Args:
            mars (Mars): The Mars environment.
        """
        current_location = self.get_location()
        free_locations = mars.get_free_adjacent_locations(current_location)

        # Filter for unvisited locations
        unvisited_locations = [loc for loc in free_locations if loc not in self.visited_locations]

        if unvisited_locations and self.battery_life >= 30:
            next_location = random.choice(unvisited_locations)
        else:
            next_location = random.choice(free_locations)

        self.visited_locations.append(next_location)
        self.__move(mars, next_location)

    def __move_towards_spacecraft(self, mars: Mars):
        """
        Move the rover towards the spacecraft location.

        Args:
            mars (Mars): The Mars environment.
        """
        self.__move_to_location(self.__space_craft_location, mars)

    def __move_to_location(self, target_location: Location, mars: Mars) -> None:
        """
        Move the rover towards the specified target location.

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
            self.__move_to_random_location(mars)

    def __remember_rocks(self, mars: Mars):
        """
        Remember rocks in adjacent cells.
        """
        adjacent_rocks = self.__scan_for_rocks_in_adjacent_cells(mars)
        for rock in adjacent_rocks:
            if rock.get_location() not in self.__remembered_rocks:
                self.__remembered_rocks.append(rock.get_location())
                print(f"Rover {self.id} detected rock at: {rock.get_location()}")

    def __scan_for_rocks_in_adjacent_cells(self, mars: Mars) -> List[Rock]:
        """
        Scans adjacent cells for rocks and returns a list of found rocks.
        Args:
            mars (Mars): The Mars environment.
        Returns:
            List[Rock]: List of rocks in adjacent cells.
        """
        adjacent_locations = mars.get_adjacent_locations(self.get_location())
        found_rocks = [mars.get_agent(loc) for loc in adjacent_locations if isinstance(mars.get_agent(loc), Rock)]
        return found_rocks

    def pick_up_rock(self, rock: Rock):
        """
        Pick up a rock from the Mars environment and remove its location from remembered rocks.
        Args:
            rock (Rock): The rock to pick up.
        """
        self.__rock = rock
        rock.picked_up = True
        self.ignore_battery = False
        if rock.get_location() in self.__remembered_rocks:
            self.__remembered_rocks.remove(rock.get_location())
        print(f"Rover {self.id} picked up rock at: {rock.get_location()}")

    def drop_rock(self) -> None:
        """
        Drop the rock the rover is carrying.
        """
        if self.__rock:
            self.__rock.set_location(self.get_location())
            self.__rock = None
            print(f"Rover {self.id} dropped a rock at {self.get_location()}.")
        else:
            print(f"Rover {self.id} has no rock to drop.")

    def has_rock(self) -> bool:
        """
        Check if the rover is carrying a rock.
        Returns:
            bool: True if the rover is carrying a rock, False otherwise.
        """
        return self.__rock is not None

    def get_remembered_rocks(self) -> List[Location]:
        """
        Get the list of remembered rock locations.
        Returns:
            List[Location]: The list of remembered rock locations.
        """
        return self.__remembered_rocks

    def clear_remembered_rocks(self) -> None:
        """
        Clear the remembered rocks list of the rover.
        """
        self.__remembered_rocks = []

    def share_battery_power(self, other_rover: Rover, mars: Mars) -> None:
        """
        Share battery power with another rover.
        Args:
            other_rover (Rover): The rover to share battery power with.
            mars (Mars): The environment.
        """
        if other_rover.get_location() in mars.get_adjacent_locations(self.get_location()):
            self.battery_life -= 5  # Deduct 5% battery from this rover and give it to the other rover
            other_rover.battery_life += 5
            print(f"Rover {self.id} shared battery power with Rover {other_rover.id}.")
            print(f"Rover {self.id} battery is {self.battery_life}%.")
            print(f"Rover {other_rover.id} battery is {other_rover.battery_life}%.")
            self.request_charging = False

    def __manage_battery(self, mars: Mars):
        """
        Manage battery life based on rover actions.
        """
        self.battery_life -= self.battery_consumption_per_move

        if self.__space_craft_location in mars.get_adjacent_locations(self.get_location()) and self.battery_life < 50:
            self.request_charging = True  # Set charging request flag
            print(f"Rover {self.id} is requesting charging at the spacecraft.")
            return  # Wait for charging, no further actions

    def sustain_damage(self, amount: int):
        """
        Sustain damage and reduce battery life.
        Args:
            amount (int): Amount of damage to sustain.
        """
        self.battery_life -= amount
        if self.battery_life <= 0:
            self.battery_life = 0
            self.damaged = True
            print(f"Rover {self.id} damaged. Can't be charged.")
            if self.has_rock():
                self.drop_rock()
        else:
            print(f"Rover {self.id} sustained damage of {amount}% from Alien. Battery Life: {self.battery_life}%.")

    def act(self, mars: Mars) -> None:
        """
        Perform an action for the rover in the Mars environment.

        Args:
            mars (Mars): The Mars environment.
        """
        if self.damaged:
            return

        if self.request_charging:
            if self.battery_life == 100:
                self.request_charging = False
                print(f"Rover {self.id} is fully charged.")
            else:
                return

        print(f"{'-' * 60}")
        print(f"Rover {self.id} - Current Location: {self.get_location()} - Battery life: {self.battery_life}%")

        if not self.ignore_battery:
            if self.battery_life <= 0:
                self.battery_life = 0
                print(f"Rover {self.id} has run out of battery and stopped at {self.get_location()}.")
                adjacent_locations = mars.get_adjacent_locations(self.get_location())
                adjacent_rovers = [mars.get_agent(loc) for loc in adjacent_locations if
                                   isinstance(mars.get_agent(loc), Rover)]
                for rover in adjacent_rovers:
                    if rover.battery_life > 30:
                        rover.share_battery_power(self, mars)
                return

        if self.target_location:
            print(f"Rover {self.id} is moving to target location: {self.target_location}.")
            adjacent_rocks = self.__scan_for_rocks_in_adjacent_cells(mars)
            target_rock = None
            for rock in adjacent_rocks:
                if rock.get_location() == self.target_location:
                    target_rock = rock
                    break  # Exit the loop once the target rock is found

            if target_rock:
                self.__move(mars, target_rock.get_location())
                self.pick_up_rock(target_rock)
                self.target_location = None
            else:
                # Check if the rover is at or adjacent to the target location
                current_location = self.get_location()
                if current_location == self.target_location or self.target_location in mars.get_adjacent_locations(
                        current_location):
                    # If the rover is at or adjacent to the target location but couldn't find the rock, reset target_location
                    print("Couldn't find the target rock")
                    self.target_location = None
                    self.ignore_battery = False
                    self.__move_towards_spacecraft(mars)
                else:
                    # Move towards the target location
                    self.__move_to_location(self.target_location, mars)

            # Exit early to avoid executing the remaining logic when the target location is being handled
            return

        # Handling rock delivery and low battery situation
        if self.__rock:
            self.__remember_rocks(mars)
            if not self.ignore_battery and self.battery_life < 30:
                print(f"Rover {self.id} is carrying a rock and has low battery.")
                self.__move_towards_spacecraft(mars)
            else:
                if self.__space_craft_location in mars.get_free_adjacent_locations(self.get_location()):
                    print(f"Rover {self.id} is adjacent to the spacecraft, ready to deliver rock.")
                    self.drop_rock()
                else:
                    self.__move_towards_spacecraft(mars)
        else:
            if not self.ignore_battery and self.battery_life < 30:
                print(f"Rover {self.id} has low battery and is moving towards the spacecraft.")
                self.__move_towards_spacecraft(mars)
            else:
                adjacent_rocks = self.__scan_for_rocks_in_adjacent_cells(mars)
                if adjacent_rocks:
                    rock_location = adjacent_rocks[0].get_location()
                    self.__move(mars, rock_location)
                    self.pick_up_rock(adjacent_rocks[0])
                else:
                    self.__move_to_explore_location(mars)

        self.__manage_battery(mars)
