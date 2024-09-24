from __future__ import annotations

from typing import TYPE_CHECKING

from model.agent import Agent
from model.environment import Environment

if TYPE_CHECKING:
    from model.location import Location


class Rock(Agent):

    def __init__(self, location: Location) -> None:
        super().__init__(location)

    def __repr__(self) -> str:
        """
        Return a string representation of the Rock object.

        Returns:
            str: A string representation of the Rock object.
        """
        return f"Rock({repr(self.get_location())})"

    def __str__(self) -> str:
        """
        Return a string describing the current location of the Rock.

        Returns:
            str: A string describing the current location of the Rock.
        """
        return f"Rock is located at: ({repr(self.get_location())})"

    def act(self, environment: Environment) -> None:
        pass
