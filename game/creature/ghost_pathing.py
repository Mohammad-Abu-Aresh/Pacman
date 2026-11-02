import random


def choose_frightened_step(
    start: tuple[int, int],
    direction: tuple[int, int],
    options: list[tuple[int, int]],
    reverse: bool,
) -> tuple[int, int] | None:
    """Choose a pseudo-random frightened turn from legal pathfinder exits.
    Try a pseudo-random preference first, then the arcade fallback order.
    Avoid reversing unless forced or the reverse is the only exit.
    made by: Mohammad Abu Aresh
    """
    order = ((0, -1), (-1, 0), (0, 1), (1, 0))
    available = set(options)
    if not available:
        return None
    reverse_step = (start[0] - direction[0], start[1] - direction[1])
    if reverse and reverse_step in available:
        return reverse_step
    preferred = random.choice(order)
    reverse_direction = (-direction[0], -direction[1])
    candidates = (preferred,) + tuple(
        move for move in order if move != preferred
    )
    for move in candidates:
        cell = (start[0] + move[0], start[1] + move[1])
        if cell in available and (
            move != reverse_direction or len(available) == 1
        ):
            return cell
    return None
