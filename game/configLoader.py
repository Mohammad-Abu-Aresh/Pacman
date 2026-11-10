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
        try:
            with open(self.fileName, "r") as f:
                content = "".join([self.__parse_line(line) for line in f])
            user_data = json.loads(content)
            if not isinstance(user_data, dict):
                print(
                    "Error: Configuration file content is not a "
                    "valid JSON object. Using default settings."
                )
                user_data = {}
        except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
            print(
                f"Error: Problem reading or parsing configuration "
                f"file '{self.fileName}' ({e}). Using default settings."
            )
            user_data = {}

        config = self.default_config.copy()
        for key, default_val in self.default_config.items():
            if key not in user_data:
                print(
                    f"Notice: '{key}' was not found in the config file. "
                    f"Using default value: {default_val}"
                )
            else:
                v = user_data[key]
                if isinstance(default_val, int) and isinstance(
                        v, str
                        ):
                    print(
                        f"Error: '{key}' must be an int, not a string! "
                        f"Using default value: {default_val}"
                    )
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
