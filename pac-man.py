from game import GameEngine
from sys import stderr


if __name__ == "__main__":
    try:
        game = GameEngine()
        game.run()

    except Exception as e:
        print(e, file=stderr)
        exit(1)
    except KeyboardInterrupt:
        exit(1)
