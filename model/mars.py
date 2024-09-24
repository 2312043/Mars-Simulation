from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

from controller.config import Config
from model.environment import Environment
from model.location import Location

if TYPE_CHECKING:
    from model.agent import Agent


class Mars(Environment):
    """Represents an environment modeled after Mars."""

    def __init__(self):
        """
        Initialise the Mars environment.

        Initialises a grid with dimensions based on the world size specified in the Config module.
        """
        super().__init__()
        self.__grid: List[List[Optional[Agent, None]]] = [
            [None for _ in range(self.get_width())] for _ in range(self.get_height())
        ]

    def clear(self) -> None:
        """Clears all agents from the grid."""
        self.__grid = [[None for _ in range(Config.world_size)] for _ in range(Config.world_size)]

    def get_agent(self, location: Location) -> Optional[Agent, None]:
        """
        Returns the agent at a given location, or None if location is None.

        Args:
            location (Location): The location to retrieve the agent from.

        Returns:
            Optional[Agent, None]: The agent at the specified location, or None if the location is outside the grid.
        """
        if location:
            wrapped_x = location.get_x() % Config.world_size
            wrapped_y = location.get_y() % Config.world_size
            return self.__grid[wrapped_y][wrapped_x]

        return None

    def get_adjacent_locations(self, location: Location) -> List[Location]:
        """
        Returns a list of adjacent positions on the grid, wrapping around the edges if necessary.

        Args:
            location (Location): The location to find adjacent positions for.

        Returns:
            List[Location]: A list of adjacent positions.
        """
        directions = [(-1, -1), (0, -1), (1, -1),
                      (-1, 0), (1, 0),
                      (-1, 1), (0, 1), (1, 1)]
        x, y = location.get_x(), location.get_y()
        return [Location((x + dx) % self.get_width(), (y + dy) % self.get_height()) for dx, dy in
                directions]

    def get_free_adjacent_locations(self, location: Location) -> List[Location]:
        """
        Returns a list of free adjacent positions on the grid, wrapping around the edges if necessary.

        Args:
            location (Location): The location to find free adjacent positions for.

        Returns:
            List[Location]: A list of free adjacent positions.
        """
        adjacent_locations = self.get_adjacent_locations(location)
        free_locations = []
        for adjacent_location in adjacent_locations:
            if self.get_agent(adjacent_location) is None:
                free_locations.append(adjacent_location)
        return free_locations

    def get_adjacent_locations_upto_3_cells(self, location: Location) -> List[Location]:
        """
        Returns a list of positions within 3 cells from the given location on the grid, wrapping around the edges if necessary.

        Args:
            location (Location): The location to find adjacent positions for.

        Returns:
            List[Location]: A list of positions within 3 cells.
        """
        x, y = location.get_x(), location.get_y()
        width, height = self.get_width(), self.get_height()

        # Generate all locations within 3 cells distance
        locations = []
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                if dx == 0 and dy == 0:
                    continue
                new_x = (x + dx) % width
                new_y = (y + dy) % height
                locations.append(Location(new_x, new_y))

        return locations

    def set_agent(self, agent: Optional[Agent, None], location: Location) -> None:
        """
        Places an agent at a specific location, wrapping around the grid edges if necessary.

        Args:
            agent (Agent): The agent to be placed.
            location (Location): The location where the agent should be placed.
        """
        if location:
            wrapped_x = location.get_x() % Config.world_size
            wrapped_y = location.get_y() % Config.world_size
            self.__grid[wrapped_y][wrapped_x] = agent
