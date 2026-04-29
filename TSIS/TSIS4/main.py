"""
main.py – entry point; all game screens live here.

Screens:
    menu        → main menu (username entry + buttons)
    playing     → delegates to game.run_game()
    gameover    → final score, retry / main menu
    leaderboard → top-10 table from DB
    settings    → toggle grid / sound, pick snake color
"""
import sys
import pygame

import config
import db
import game as game_mod
import settings as settings_mod

# ── Pygame init ───────────────────────────────────────────────────────────────
pygame.init()
surface = pygame.display.set_mode((config.WINDOW_W, config.WINDOW_H))
pygame.display.set_caption("Snake  —  TSIS 3")
clock = pygame.time.Clock()

# ── Fonts ─────────────────────────────────────────────────────────────────────
F_TITLE  = pygame.font.SysFont("consolas", 48, bold=True)
F_BIG    = pygame.font.SysFont("consolas", 32)
F_MED    = pygame.font.SysFont("consolas", 22)
F_SM     = pygame.font.SysFont("consolas", 17)

# ── DB init ───────────────────────────────────────────────────────────────────
db.init_db()

# ── User settings ─────────────────────────────────────────────────────────────
user_settings = settings_mod.load()


# ═════════════════════════════════════════════════════════════════════════════
#  Shared UI helpers
# ═════════════════════════════════════════════════════════════════════════════

def draw_text(text, font, color, cx, cy):
    surf = font.render(text, True, color)
    r = surf.get_rect(center=(cx, cy))
    surface.blit(surf, r)
    return r


def draw_button(text, font, x, y, w, h, idle_col, hover_col):
    mx, my = pygame.mouse.get_pos()
    rect = pygame.Rect(x, y, w, h)
    col  = hover_col if rect.collidepoint(mx, my) else idle_col
    pygame.draw.rect(surface, col, rect, border_radius=6)
    pygame.draw.rect(surface, config.WHITE, rect, 2, border_radius=6)
    draw_text(text, font, config.WHITE, rect.centerx, rect.centery)
    return rect


def btn_clicked(rect) -> bool:
    mx, my = pygame.mouse.get_pos()
    return rect.collidepoint(mx, my)


# ═════════════════════════════════════════════════════════════════════════════
#  MAIN MENU
# ═════════════════════════════════════════════════════════════════════════════

def screen_menu():
    username   = ""
    typing     = True          # focus on text input by default
    CX         = config.WINDOW_W // 2

    while True:
        surface.fill(config.BLACK)

        draw_text("🐍  SNAKE", F_TITLE, config.GREEN, CX, 70)

        # Username prompt
        draw_text("Enter username:", F_MED, config.LIGHT_GREY, CX, 150)
        input_rect = pygame.Rect(CX - 150, 170, 300, 36)
        pygame.draw.rect(surface, (30, 30, 30), input_rect, border_radius=4)
        border_col = config.GREEN if typing else config.DARK_GREY
        pygame.draw.rect(surface, border_col, input_rect, 2, border_radius=4)
        uname_surf = F_MED.render(username + ("|" if typing else ""), True, config.WHITE)
        surface.blit(uname_surf, (input_rect.x + 8, input_rect.y + 6))

        # Buttons
        btn_play  = draw_button("Play",         F_MED, CX-100, 230, 200, 42,
                                (0, 120, 0), (0, 180, 0))
        btn_lb    = draw_button("Leaderboard",  F_MED, CX-100, 285, 200, 42,
                                (0,  60, 120), (0, 90, 170))
        btn_cfg   = draw_button("Settings",     F_MED, CX-100, 340, 200, 42,
                                (80,  50, 0), (130, 80, 0))
        btn_quit  = draw_button("Quit",         F_MED, CX-100, 395, 200, 42,
                                (120,  0, 0), (190, 0, 0))

        hint = "Click the name field to type your username, then press Play."
        draw_text(hint, F_SM, config.DARK_GREY, CX, config.WINDOW_H - 14)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_rect.collidepoint(event.pos):
                    typing = True
                else:
                    typing = False

                if btn_clicked(btn_play):
                    name = username.strip() or "Player"
                    return "playing", name

                if btn_clicked(btn_lb):
                    return "leaderboard", username.strip() or "Player"

                if btn_clicked(btn_cfg):
                    return "settings", username.strip() or "Player"

                if btn_clicked(btn_quit):
                    pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN and typing:
                if event.key == pygame.K_RETURN:
                    typing = False
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                else:
                    if len(username) < 20 and event.unicode.isprintable():
                        username += event.unicode

        clock.tick(30)


# ═════════════════════════════════════════════════════════════════════════════
#  GAME OVER SCREEN
# ═════════════════════════════════════════════════════════════════════════════

def screen_gameover(username, player_id, score, level, personal_best):
    CX = config.WINDOW_W // 2
    # Update personal best if needed
    new_best = max(personal_best, score)

    while True:
        surface.fill(config.BLACK)

        draw_text("GAME OVER", F_TITLE, config.RED,    CX, 80)
        draw_text(f"Score  : {score}",        F_BIG, config.WHITE,  CX, 165)
        draw_text(f"Level  : {level}",        F_BIG, config.YELLOW, CX, 205)
        draw_text(f"Best   : {new_best}",     F_BIG, config.GOLD,   CX, 245)
        draw_text(f"Player : {username}",     F_MED, config.LIGHT_GREY, CX, 280)

        btn_retry = draw_button("Retry",     F_MED, CX-110, 320, 200, 42,
                                (0, 120, 0), (0, 180, 0))
        btn_menu  = draw_button("Main Menu", F_MED, CX-110, 375, 200, 42,
                                (0, 60, 120), (0, 90, 170))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_clicked(btn_retry):
                    return "playing", username, new_best
                if btn_clicked(btn_menu):
                    return "menu", username, new_best

        clock.tick(30)


# ═════════════════════════════════════════════════════════════════════════════
#  LEADERBOARD SCREEN
# ═════════════════════════════════════════════════════════════════════════════

def screen_leaderboard(username):
    rows  = db.get_top10()
    CX    = config.WINDOW_W // 2
    col_x = [40, 100, 260, 380, 490, 640]  # rank, user, score, level, date, (pad)

    while True:
        surface.fill(config.BLACK)
        draw_text("🏆  TOP 10 LEADERBOARD", F_BIG, config.GOLD, CX, 30)

        # Header
        headers = ["#", "Username", "Score", "Level", "Date"]
        hy = 70
        for i, h in enumerate(headers):
            surface.blit(F_SM.render(h, True, config.YELLOW), (col_x[i], hy))
        pygame.draw.line(surface, config.DARK_GREY, (30, hy + 20), (config.WINDOW_W - 30, hy + 20), 1)

        # Rows
        if not rows:
            draw_text("No records yet — play a game!", F_MED, config.LIGHT_GREY, CX, 180)
        else:
            for ri, row in enumerate(rows):
                ry = hy + 28 + ri * 26
                col = config.GOLD if ri == 0 else (config.LIGHT_GREY if ri < 3 else config.WHITE)
                date_str = row["played_at"].strftime("%m/%d %H:%M") if row.get("played_at") else "-"
                cells = [
                    str(row["rank"]),
                    str(row["username"])[:12],
                    str(row["score"]),
                    str(row["level_reached"]),
                    date_str,
                ]
                for ci, cell in enumerate(cells):
                    surface.blit(F_SM.render(cell, True, col), (col_x[ci], ry))

        btn_back = draw_button("Back", F_MED, CX - 60, config.WINDOW_H - 60, 120, 38,
                               (80, 50, 0), (130, 80, 0))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_clicked(btn_back):
                    return "menu", username

        clock.tick(30)


# ═════════════════════════════════════════════════════════════════════════════
#  SETTINGS SCREEN
# ═════════════════════════════════════════════════════════════════════════════

COLOR_OPTIONS = [
    ("Green",   (0, 200, 0)),
    ("Cyan",    (0, 255, 255)),
    ("Blue",    (50, 100, 255)),
    ("Orange",  (255, 165, 0)),
    ("White",   (230, 230, 230)),
    ("Pink",    (255, 105, 180)),
]


def screen_settings(username):
    global user_settings
    # Work on a local copy so we can cancel (we always save here though)
    cfg = dict(user_settings)
    CX  = config.WINDOW_W // 2

    while True:
        surface.fill(config.BLACK)
        draw_text("⚙  SETTINGS", F_BIG, config.LIGHT_GREY, CX, 30)

        # Grid toggle
        grid_label = "Grid Overlay:  ON" if cfg["grid_overlay"] else "Grid Overlay:  OFF"
        btn_grid = draw_button(grid_label, F_MED, CX - 130, 90, 260, 40,
                               (40, 40, 80), (60, 60, 120))

        # Sound toggle
        snd_label = "Sound:  ON" if cfg["sound"] else "Sound:  OFF"
        btn_snd = draw_button(snd_label, F_MED, CX - 130, 145, 260, 40,
                              (40, 40, 80), (60, 60, 120))

        # Snake color picker
        draw_text("Snake Color:", F_MED, config.LIGHT_GREY, CX, 205)
        color_rects = []
        sw = 60
        total_w = len(COLOR_OPTIONS) * (sw + 10) - 10
        sx_start = CX - total_w // 2
        for ci, (cname, cval) in enumerate(COLOR_OPTIONS):
            rx = sx_start + ci * (sw + 10)
            ry = 220
            rect = pygame.Rect(rx, ry, sw, 30)
            pygame.draw.rect(surface, cval, rect, border_radius=4)
            if list(cval) == cfg["snake_color"] or tuple(cval) == tuple(cfg["snake_color"]):
                pygame.draw.rect(surface, config.WHITE, rect, 3, border_radius=4)
            color_rects.append((rect, cval))
            lbl = F_SM.render(cname, True, config.WHITE)
            surface.blit(lbl, (rx + sw // 2 - lbl.get_width() // 2, ry + 33))

        # Preview snake
        sc = tuple(cfg["snake_color"])
        draw_text("Preview:", F_SM, config.LIGHT_GREY, CX, 310)
        for i in range(6):
            pygame.draw.rect(surface, sc,
                             pygame.Rect(CX - 30 + i * 12, 325, 10, 10))

        btn_save = draw_button("Save & Back", F_MED, CX - 100, 380, 200, 42,
                               (0, 100, 50), (0, 160, 80))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_clicked(btn_grid):
                    cfg["grid_overlay"] = not cfg["grid_overlay"]
                if btn_clicked(btn_snd):
                    cfg["sound"] = not cfg["sound"]
                for crect, cval in color_rects:
                    if crect.collidepoint(event.pos):
                        cfg["snake_color"] = list(cval)
                if btn_clicked(btn_save):
                    user_settings = cfg
                    settings_mod.save(cfg)
                    return "menu", username

        clock.tick(30)


# ═════════════════════════════════════════════════════════════════════════════
#  STATE MACHINE
# ═════════════════════════════════════════════════════════════════════════════

def main():
    state        = "menu"
    username     = "Player"
    player_id    = None
    personal_best = 0

    while True:
        if state == "menu":
            state, username = screen_menu()
            # Resolve DB player
            player_id     = db.get_or_create_player(username)
            personal_best = db.get_personal_best(player_id) if player_id else 0

        elif state == "playing":
            next_state, score, level = game_mod.run_game(
                surface, clock, username, player_id, personal_best, user_settings
            )
            # Save to DB
            if player_id:
                db.save_session(player_id, score, level)
            personal_best = max(personal_best, score)
            state = next_state
            _score, _level = score, level  # keep for game-over screen

        elif state == "gameover":
            state, username, personal_best = screen_gameover(
                username, player_id, _score, _level, personal_best
            )
            if state == "playing":
                # resolve again in case username changed (it doesn't here, but keep clean)
                player_id = db.get_or_create_player(username)

        elif state == "leaderboard":
            state, username = screen_leaderboard(username)

        elif state == "settings":
            state, username = screen_settings(username)

        else:
            state = "menu"


if __name__ == "__main__":
    main()
