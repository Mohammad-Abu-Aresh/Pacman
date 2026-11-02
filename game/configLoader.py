import json
import sys
from typing import Any


class ConfigLoader:

    def __init__(self) -> None:
        """
        Read the configuration path from the command-line arguments.
        Prepare default settings and an empty data container.
        made by: Abdalghani Abtah
        update by: Mohammad Abu Aresh
        """
        self.fileName: str = sys.argv[1]
        self.default_config: dict[str, Any] = {
            "highscore_filename": "highscores.json",
            "lives": 3,
            "pacgum": 42,
            "points_per_pacgum": 10,
            "points_per_super_pacgum": 50,
            "points_per_ghost": 200,
            "seed": 42,
            "level_max_time": 90,
            "max_levels": 10
        }
        self.data: dict[str, Any] = {}

    @property
    def load_config(self) -> dict[str, Any]:
        """
        Load JSON settings, ignore comment lines, and merge
        supported keys.
        Check configured value types and validate the maximum level
        count.
        made by: Abdalghani Abtah
        update by: Mohammad Abu Aresh
        """
        with open(self.fileName, "r") as f:
            content = "".join([self.__parse_line(line) for line in f])
        user_data = json.loads(content)

        config = self.default_config.copy()  # rename key, value
        for key, v in user_data.items():
            if key in config:
                if isinstance(self.default_config[key], int) and isinstance(
                        v, str
                        ):
                    print(f"Error: '{key}' must be an int, not a string!")
                    continue
                config[key] = v
        if config["max_levels"] < 3 or config["max_levels"] > 15:
            raise ValueError(
                f"Error: 'max_levels' must be between 3 and 15, "
                f"got {config['max_levels']}"
            )
        return config

    def __parse_line(self, line: str) -> str:
        """
        Remove full-line comments from the configuration text.
        Return every other line unchanged for JSON parsing.
        made by: Abdalghani Abtah
        """
        if line.strip().startswith("#"):
            return ""
        return line
