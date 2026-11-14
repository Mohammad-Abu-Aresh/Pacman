HARDCORE_SCORE_MULTIPLIER = 1.3


def final_score(points: int, hardcore: bool) -> int:
    """
    Convert the collected points to the final score of the game.
    Multiply them in hardcore mode and keep them unchanged otherwise.
    made by: Mohammad Abu Aresh
    """
    if not hardcore:
        return points
    return round(points * HARDCORE_SCORE_MULTIPLIER)


def score_multiplier_label(hardcore: bool) -> str:
    """
    Return the text shown next to the score counter.
    Show the multiplier in hardcore mode and nothing otherwise.
    made by: Mohammad Abu Aresh
    """
    return f"x {HARDCORE_SCORE_MULTIPLIER}" if hardcore else ""
