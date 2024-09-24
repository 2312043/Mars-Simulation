class Location:
    """Represents a location with integer x and y coordinates."""

    def __init__(self, x: int, y: int) -> None:
        """
        Initialise the Location object with the given x and y coordinates.

        Parameters:
            x (int): The x-coordinate of the location.
            y (int): The y-coordinate of the location.
        """
        self.__x = x
        self.__y = y

    def __eq__(self, other):
        """Return true if two objects are equal."""
        return self.__x == other.get_x() and self.__y == other.get_y()

    def __repr__(self) -> str:
        """Return a string representation of the location."""
        return f"Location({self.__x}, {self.__y})"

    def __str__(self) -> str:
        """Return a string representation of the location."""
        return f"Located at ({self.__x}, {self.__y})"

    def get_x(self) -> int:
        """Get the x-coordinate of the location."""
        return self.__x

    def set_x(self, x: int) -> None:
        """
        Set the x-coordinate of the location.

        Parameters:
            x (int): The new x-coordinate of the location.
        """
        self.__x = x

    def get_y(self) -> int:
        """Get the y-coordinate of the location."""
        return self.__y

    def set_y(self, y: int) -> None:
        """
        Set the y-coordinate of the location.

        Parameters:
            y (int): The new y-coordinate of the location.
        """
        self.__y = y
