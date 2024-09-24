from __future__ import annotations

import math
import random
from typing import List, TYPE_CHECKING

from model.agent import Agent
from model.rover import Rover
from controller.config import Config

if TYPE_CHECKING:
    from model.location import Location
    from model.mars import Mars


class Spacecraft(Agent):

    def __init__(self, location: Location):
        super().__init__(location)
        self.retrieved_rock_locations: List[Location] = []
        self.target_locations: List[Location] = []
        self.rovers: List[Rover] = []
        self.rovers_initialized = False

    def __scan_for_rovers_in_adjacent_cells(self, mars: Mars) -> List[Rover]:
        """
        Scans adjacent cells for rovers and returns a list of found rovers.
        """
        adjacent_locations = mars.get_adjacent_locations(self.get_location())
        found_rovers = []
        for adjacent_location in adjacent_locations:
            agent = mars.get_agent(adjacent_location)
            if isinstance(agent, Rover):
                found_rovers.append(agent)
                if agent not in self.rovers:
                    self.rovers.append(agent)
        return found_rovers

    def __retrieve_rocks_from_rover(self, mars: Mars, rover: Rover) -> None:
        """
        Retrieve rocks from a rover adjacent to the spacecraft.
        """
        if rover.has_rock():
            rock_location = rover.get_location()
            self.retrieved_rock_locations.append(rock_location)
            rover.drop_rock()  # Rover drops the rock it is carrying
            print(f"Spacecraft retrieved a rock from rover at location: {rock_location}")
            print(f"The spacecraft has retrieved {len(self.retrieved_rock_locations)} rocks.")
            print(f"{'-' * 60}")

    def __find_nearest_rock_location(self, target_locations: List[Location]) -> Location:
        """
        Finds the nearest rock location from the list of target locations using Manhattan distance.
        """
        spacecraft_location = self.get_location()
        nearest_location = None
        min_distance = float('inf')
        for location in target_locations:
            distance = abs(spacecraft_location.get_x() - location.get_x()) + abs(
                spacecraft_location.get_y() - location.get_y())
            if distance < min_distance:
                min_distance = distance
                nearest_location = location
        return nearest_location

    @staticmethod
    def __calculate_distance(location1: Location, location2: Location) -> int:
        """
        Calculate Manhattan distance between two locations.
        """
        return abs(location1.get_x() - location2.get_x()) + abs(location1.get_y() - location2.get_y())

    def __form_rover_team(self, mars: Mars, rock_location: Location) -> List[Rover]:
        """
        Form a team of rovers to fetch a distant rock.
        """
        found_rovers = self.__scan_for_rovers_in_adjacent_cells(mars)
        available_rovers = [rover for rover in found_rovers if not rover.has_rock() and rover.request_charging]

        team = []
        distance = self.__calculate_distance(self.get_location(), rock_location)
        required_rovers = math.ceil(distance / 7)

        if len(available_rovers) >= required_rovers:
            team = available_rovers[:required_rovers]

        return team

    @staticmethod
    def __instruct_rover_team(team: List[Rover], rock_location: Location) -> None:
        """
        Instruct the team of rovers to fetch the rock.
        """
        team[0].ignore_battery = True
        team[0].battery_life = 100
        print(f"Rover {team[0].id} is ignoring battery.")
        team[1].battery_life = 90
        for rover in team:
            rover.target_location = rock_location
            print(f"Rover {rover.id} instructed to fetch rock from {rock_location} with as a Team")

    def create_new_rover(self, mars: Mars):
        if len(self.rovers) < Config.initial_num_rovers and len(self.retrieved_rock_locations) >= 100:
            # Remove 100 rocks from the retrieved rock list
            self.retrieved_rock_locations = self.retrieved_rock_locations[100:]

            # Create a new rover at the spacecraft location
            free_locations = mars.get_free_adjacent_locations(self.get_location())
            if len(free_locations) > 0:
                rover_location = random.choice(free_locations)
                rover = Rover(rover_location, self.get_location())
                mars.set_agent(rover, rover_location)
                self.rovers.append(rover)

                print(f"Created new Rover {rover.id}.")

    def act(self, mars: Mars) -> None:
        if not self.rovers_initialized:
            self.__scan_for_rovers_in_adjacent_cells(mars)
            self.rovers_initialized = True

        if len(self.rovers) < Config.initial_num_rovers:
            self.create_new_rover(mars)

        found_rovers = self.__scan_for_rovers_in_adjacent_cells(mars)
        print(f"{'-' * 60}")
        print(f"Spacecraft - Current Location: {self.get_location()}")
        print(f"Spacecraft detected the following rovers: {[rover.id for rover in found_rovers]}")

        for rover in found_rovers:
            print(
                f"Rover {rover.id} status - Battery: {rover.battery_life}, Has rock: {rover.has_rock()}, Requesting charging: {rover.request_charging}, Target Location: {rover.target_location}")

            if rover.has_rock():
                self.__retrieve_rocks_from_rover(mars, rover)
                # Ensure rover remains active after dropping rock
                print(
                    f"Rover {rover.id} dropped rock. Battery life: {rover.battery_life}, Requesting charging: {rover.request_charging}")

            if rover.request_charging:
                rover.battery_life += 5
                if rover.battery_life > 100:
                    rover.battery_life = 100
                print(f"Rover {rover.id} is being charged. Battery life: {rover.battery_life}%")
                # Check if fully charged and reset request_charging if necessary
                if rover.battery_life >= 100:
                    rover.request_charging = False
                    print(f"Rover {rover.id} is fully charged.")

        rover_target_locations = []
        for rover in found_rovers:
            rover_target_locations.extend(rover.get_remembered_rocks())

        if rover_target_locations:
            for location in rover_target_locations:
                if location not in self.target_locations:
                    self.target_locations.append(location)
            print(f"Spacecraft has the following target locations: {self.target_locations}")
            nearest_rock_location = self.__find_nearest_rock_location(self.target_locations)

            if self.__calculate_distance(self.get_location(), nearest_rock_location) > 7:
                team = self.__form_rover_team(mars, nearest_rock_location)
                if len(team) > 1:  # Ensure that a full team is formed
                    self.__instruct_rover_team(team, nearest_rock_location)
            else:
                # Direct the first available rover to the nearest rock location
                for rover in found_rovers:
                    if not rover.target_location and not rover.has_rock() and not rover.request_charging:
                        rover.target_location = nearest_rock_location
                        print(f"Rover {rover.id} directed to the nearest rock location at: {nearest_rock_location}")
                        break

            for rover in found_rovers:
                rover.clear_remembered_rocks()
            self.target_locations.remove(nearest_rock_location)
            print(f"{'-' * 60}")
