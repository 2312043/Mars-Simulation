from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING

from controller.config import Config

if TYPE_CHECKING:
    from model.agent import Agent
    from model.location import Location


class Environment(ABC):
    """Abstract class representing an environment."""

    def __init__(self) -> None:
        """
        Initialise the Environment object.

        Initialises the height and width of the environment based on Config.world_size.
        """
        self.__height = Config.world_size
        self.__width = Config.world_size

    def __repr__(self) -> str:
        """
        Return a string representation of the Environment object.

        Returns:
            str: A string representation of the Environment object including its height and width.
        """
        return f"Environment(height:{self.__height}, width:{self.__width})"

    def __str__(self) -> str:
        """
        Return a string describing the dimensions of the environment.

        Returns:
            str: A string describing the dimensions of the environment.
        """
        return f"Environment dimensions are {self.__width}x{self.__height} cells."

    @abstractmethod
    def clear(self) -> None:
        """
        Clears the environment.
        """
        pass

    @abstractmethod
    def get_agent(self, location: Location) -> Optional[Agent]:
        """
        Retrieve the agent at the specified location in the environment.

        Args:
            location (Location): The specified location of the agent.

        Returns:
            Agent: The agent at the specified location.
        """
        pass

    def get_height(self) -> int:
        """
        Get the height of the environment.

        Returns:
            int: The height of the environment.
        """
        return self.__height

    def get_width(self) -> int:
        """
        Get the width of the environment.

        Returns:
            int: The width of the environment.
        """
        return self.__width

    @abstractmethod
    def set_agent(self, agent: Agent, location: Location) -> None:
        """
        Set the agent at the specified location in the environment.

        Args:
            agent (Agent): The agent to be added to the environment.
            location (Location): The specified location of the agent.
        """
        pass
