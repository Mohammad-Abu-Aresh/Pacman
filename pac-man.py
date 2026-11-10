from game import GameEngine, ConfigLoader
from sys import stderr


if __name__ == "__main__":

    try:
        config = ConfigLoader().load_config
        game = GameEngine(config)
        game.run()
    except Exception as e:
        print(e, file=stderr)
        exit(1)
    except BaseException as e:
        print(e, file=stderr)
        exit(1)
    except KeyboardInterrupt:
        print("Game interrupted by user.", file=stderr)
        exit(1)
