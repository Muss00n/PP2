"""
main.py – entry point for Road Racer.

Wires together the screens from ui.py and the game loop from racer.py.
Run with:  python main.py
"""
import pygame, sys

# racer.py must be imported first — it calls pygame.init() and
# creates DISPLAY/clock, which ui.py then imports.
from racer import cfg, run_game
from ui    import ask_username, main_menu, leaderboard_screen, settings_screen, game_over_screen


def main() -> None:
    username = cfg.get("username", "Player")

    while True:
        action = main_menu()

        if action == "quit":
            pygame.quit(); sys.exit()

        elif action == "board":
            leaderboard_screen()

        elif action == "settings":
            settings_screen()

        elif action == "play":
            username = ask_username()

            # Inner loop: keep playing until the user chooses MENU
            while True:
                score, coins, dist, hp = run_game(username)
                result = game_over_screen(score, coins, dist, username, hp)
                if result == "menu":
                    break
                # result == "retry" → loop back and start a new round


if __name__ == "__main__":
    main()
