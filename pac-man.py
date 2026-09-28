from game import GameEngine, ConfigLoader
from sys import stderr


if __name__ == "__main__":
    config = ConfigLoader().load_config
    game = GameEngine(config)
    game.run()
    try:
        ...
    except Exception as e:
        print(e, file=stderr)
        exit(1)
    except KeyboardInterrupt:
        exit(1)
