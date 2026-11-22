NAME_LIMIT = 10
DEFAULT_NAME = "Player"
BLINK_MILLISECONDS = 500


def add_character(text: str, char: str) -> str:
    """
    Append one typed character to the name when it is allowed.
    Ignore keys without a character, controls and extra spaces.
    made by: Mohammad Abu Aresh
    """
    if len(char) != 1 or not char.isprintable():
        return text
    if len(text) >= NAME_LIMIT:
        return text
    if char.isspace() and (not text or text.endswith(" ")):
        return text
    return text + char


def remove_character(text: str) -> str:
    """
    Remove the last typed character of the name.
    Return an empty name unchanged.
    made by: Mohammad Abu Aresh
    """
    return text[:-1]


def final_name(text: str) -> str:
    """
    Return the name that is saved with the final score.
    Trim the spaces and use a default name when nothing was typed.
    made by: Mohammad Abu Aresh
    """
    return text.strip() or DEFAULT_NAME


def cursor_text(text: str, ticks: int) -> str:
    """
    Return the typed name followed by a blinking cursor.
    Show the cursor for half a second and hide it for half a second.
    made by: Mohammad Abu Aresh
    """
    shown = (ticks // BLINK_MILLISECONDS) % 2 == 0
    return text + ("|" if shown else "")


def visible_text_area(text_width: int, box_width: int) -> tuple[int, int]:
    """
    Return the part of a rendered text that fits inside the box.
    Keep the end of the text visible so the newest letters show.
    made by: Mohammad Abu Aresh
    """
    if text_width <= box_width:
        return 0, text_width
    return text_width - box_width, box_width
