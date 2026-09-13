import json
import sys


class ConfigLoader:

    def __init__(self) -> None:
        self.fileName: str = sys.argv[1]
        self.data: dict = {}

    @property
    def load_config(self) -> dict:
        with open(self.filepath, "r") as f:
            content = "".join([self.__parse_line(l) for l in f])
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
                return config

    def __parse_line(self, line: str) -> str:
        if line.strip().startswith("#"):
            return ""
        return line
