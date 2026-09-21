import json
import sys
from typing import Any


class ConfigLoader:

    def __init__(self) -> None:
        self.fileName: str = sys.argv[1]
        self.default_config = {
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
        with open(self.fileName, "r") as f:
            content = "".join([self.__parse_line(line) for line in f])
        user_data = json.loads(content)

        config = self.default_config.copy()
        for k, v in user_data.items():
            if k in config:
                if isinstance(self.default_config[k], int) and isinstance(
                        v, str
                        ):
                    print(f"Error: '{k}' must be an int, not a string!")
                    continue
                config[k] = v
        if config["max_levels"] < 3 or config["max_levels"] > 15:
            raise ValueError(
                f"Error: 'max_levels' must be between 3 and 15, "
                f"got {config['max_levels']}"
            )
        return config

    def __parse_line(self, line: str) -> str:
        if line.strip().startswith("#"):
            return ""
        return line
