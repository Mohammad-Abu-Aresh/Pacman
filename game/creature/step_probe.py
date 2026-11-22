import math

PROBE_DISTANCE = 0.5


def _ahead(value: float, direction: int) -> int:
    """
    Return the cell index half a cell ahead of a coordinate.
    Treat the cell border as part of the cell in the moving direction.
    made by: Mohammad Abu Aresh
    """
    if direction > 0:
        return math.floor(value + PROBE_DISTANCE + 0.5)
    if direction < 0:
        return math.ceil(value - PROBE_DISTANCE - 0.5)
    return round(value)


def probe_cell(x: float, y: float, dx: int, dy: int) -> tuple[int, int]:
    """
    Return the grid cell half a cell ahead in the moving direction.
    Use it to find a wall before the walker leaves the cell center.
    made by: Mohammad Abu Aresh
    """
    return _ahead(x, dx), _ahead(y, dy)
