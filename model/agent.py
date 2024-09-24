from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from model.environment import Environment
    from model.location import Location


class Agent(ABC):
    """Represents an agent with a location."""

    def __init__(self, location: Location) -> None:
        """
        Initialise the Agent object with the given location.

        Parameters:
            location (Location): The location of the agent.
        """
        self.__location = location

    def __eq__(self, other: 'Agent') -> bool:
        """
        Compare two Agent objects for equality based on their locations.

        Parameters:
            other (Agent): The other Agent object to compare.

        Returns:
            bool: True if the two agents have the same location, False otherwise.
        """
        return isinstance(other, Agent) and self.__location == other.__location

    def __str__(self) -> str:
        """
        Return a string representation of the Agent object.

        Returns:
            str: String representation of the Agent object.
        """
        return f"Agent at {self.__location}"

    @abstractmethod
    def act(self, environment: Environment) -> None:
        pass

    def get_location(self) -> Location:
        """
        Get the location of the agent.

        Returns:
            Location: The location of the agent.
        """
        return self.__location

    def set_location(self, location: Location) -> None:
        """
        Set the location of the agent.

        Parameters:
            location (Location or None): The new location of the agent.
        """
        self.__location = location
