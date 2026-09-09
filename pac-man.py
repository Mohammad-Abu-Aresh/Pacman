from game import GameEngine

if __name__ == "__main__":
    try:
        game = GameEngine()
        game.run()
    except Exception:
        exit(1)
    except KeyboardInterrupt:
        exit(1)
