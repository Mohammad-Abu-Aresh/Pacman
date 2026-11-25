from sys import stderr
import sys


if __name__ == "__main__":

    try:
        from game import GameEngine, ConfigLoader
        config = ConfigLoader().load_config
        game = GameEngine(config)
        game.run()
    except ModuleNotFoundError as e:
        print(f"Module not found: {e}", file=stderr)
        sys.exit(1)
    except Exception as e:
        print(e, file=stderr)
        sys.exit(1)
    except BaseException as e:
        print(e, file=stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("Game interrupted by user.", file=stderr)
        sys.exit(1)
