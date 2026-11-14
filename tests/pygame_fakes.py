from collections.abc import Iterator
from types import SimpleNamespace
from typing import Any


class KeyState:
    def __init__(self, flags: tuple[bool, ...]) -> None:
        """Store the key flags of one fake frame.
        Mimic the pygame key state that can only be indexed.
        made by: Mohammad Abu Aresh
        """
        self.flags = flags

    def __getitem__(self, index: int) -> bool:
        """Return whether the key at this index is pressed.
        Index it like the real pygame key state.
        made by: Mohammad Abu Aresh
        """
        return self.flags[index]

    def __iter__(self) -> Iterator[bool]:
        """Refuse iteration like recent pygame versions do.
        Raise the same message the game crashed with.
        made by: Mohammad Abu Aresh
        """
        raise TypeError("Iterating over key states is not supported")


def fake_pygame(pressed: set[str]) -> Any:
    """Create a stand in for pygame with a chosen set of pressed keys.
    The key state is a plain tuple indexed by the fake key constants.
    made by: Mohammad Abu Aresh
    """
    index = {"h": 0, "esc": 1, "n": 2, "x": 3}
    flags = tuple(i in {index[name] for name in pressed} for i in range(4))
    return SimpleNamespace(
        key=SimpleNamespace(get_pressed=lambda: KeyState(flags)),
        K_h=0,
        K_ESCAPE=1,
        K_n=2,
    )
