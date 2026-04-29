"""
ui.py – all game screens for Road Racer.

Imports shared state (DISPLAY, clock, cfg, fonts, colours, helpers)
from racer.py so there is a single source of truth for every constant.
"""
import pygame, sys
from pygame.locals import QUIT, KEYDOWN, MOUSEBUTTONDOWN, K_RETURN, K_BACKSPACE

from racer import (
    DISPLAY, clock, cfg,
    W, H, FPS,
    F_BIG, F_MID, F_SM, F_XS,
    WHITE, RED, GOLD, GREEN, GRAY, DARK, ACCENT,
    CAR_TINTS, ScrollBG,
    txt, button, btn_clicked, panel,
)
from persistence import load_leaderboard, save_settings, save_score


# ══════════════════════════════════════════════════════════════════════════════
#  Username entry
# ══════════════════════════════════════════════════════════════════════════════

def ask_username() -> str:
    """Full-screen username entry. Returns the confirmed name."""
    name = cfg.get("username", "")
    bg   = ScrollBG()

    while True:
        bg.update(3)
        bg.draw(DISPLAY)

        ov = pygame.Surface((W, H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 160))
        DISPLAY.blit(ov, (0, 0))

        txt(DISPLAY, "Enter Name",           F_MID, ACCENT, W//2, 180)
        box = pygame.Rect(80, 240, 240, 44)
        pygame.draw.rect(DISPLAY, (50,50,50), box, border_radius=8)
        pygame.draw.rect(DISPLAY, ACCENT,     box, 2, border_radius=8)
        txt(DISPLAY, name + "|",             F_MID, WHITE, W//2, 262)
        txt(DISPLAY, "Press ENTER to start", F_XS,  GRAY,  W//2, 310)

        pygame.display.update()
        clock.tick(FPS)

        for e in pygame.event.get():
            if e.type == QUIT: pygame.quit(); sys.exit()
            if e.type == KEYDOWN:
                if e.key == K_RETURN and name.strip():
                    cfg["username"] = name.strip()
                    save_settings(cfg)
                    return name.strip()
                elif e.key == K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 14 and e.unicode.isprintable():
                    name += e.unicode


# ══════════════════════════════════════════════════════════════════════════════
#  Main menu
# ══════════════════════════════════════════════════════════════════════════════

def main_menu() -> str:
    """Returns one of: 'play', 'board', 'settings', 'quit'."""
    bg = ScrollBG()
    bw, bh = 200, 44
    cx = W // 2
    rects = {
        n: pygame.Rect(cx - bw//2, y, bw, bh)
        for n, y in [("play",230), ("board",285), ("settings",340), ("quit",395)]
    }
    labels = {"play":"PLAY", "board":"LEADERBOARD", "settings":"SETTINGS", "quit":"QUIT"}

    while True:
        bg.update(3)
        bg.draw(DISPLAY)

        ov = pygame.Surface((W, H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 140))
        DISPLAY.blit(ov, (0, 0))

        txt(DISPLAY, "RACER",                    F_BIG, ACCENT, cx, 120)
        txt(DISPLAY, "Dodge · Collect · Survive", F_XS,  GRAY,  cx, 170)
        for k, r in rects.items():
            button(DISPLAY, r, labels[k], F_SM)

        pygame.display.update()
        clock.tick(FPS)

        for e in pygame.event.get():
            if e.type == QUIT: pygame.quit(); sys.exit()
            for k, r in rects.items():
                if btn_clicked(e, r): return k


# ══════════════════════════════════════════════════════════════════════════════
#  Leaderboard screen
# ══════════════════════════════════════════════════════════════════════════════

def leaderboard_screen() -> None:
    """Top-10 table; blocks until the user presses BACK."""
    board = load_leaderboard()
    back  = pygame.Rect(W//2 - 80, 545, 160, 40)

    while True:
        DISPLAY.fill(DARK)
        panel(DISPLAY, 30, 70, W-60, 460)

        txt(DISPLAY, "TOP 10", F_MID, ACCENT, W//2, 45)

        if not board:
            txt(DISPLAY, "No scores yet", F_SM, GRAY, W//2, 290)
        else:
            hdr = F_XS.render(
                f"{'#':<3}{'Name':<10}{'Sc':>5}{'Dst':>5}{'Cn':>4}{'HP':>4}{'Dif':<7}", True, ACCENT
            )
            DISPLAY.blit(hdr, (45, 85))
            pygame.draw.line(DISPLAY, ACCENT, (45, 104), (370, 104), 1)
            for i, e in enumerate(board):
                col = GOLD if i == 0 else (WHITE if i < 3 else GRAY)
                coins = e.get("coins", 0)
                hp    = e.get("hp", 0)
                diff  = e.get("difficulty", "?")[:3]
                row = F_XS.render(
                    f"{i+1:<3}{e['name']:<10}{e['score']:>5}{e['dist']:>5}{coins:>4}{hp:>4} {diff}",
                    True, col,
                )
                DISPLAY.blit(row, (45, 110 + i*30))

        button(DISPLAY, back, "BACK", F_SM)
        pygame.display.update()
        clock.tick(FPS)

        for e in pygame.event.get():
            if e.type == QUIT: pygame.quit(); sys.exit()
            if btn_clicked(e, back): return


# ══════════════════════════════════════════════════════════════════════════════
#  Settings screen
# ══════════════════════════════════════════════════════════════════════════════

def settings_screen() -> None:
    """Mutates cfg in place; saves to disk on exit."""
    diffs = ["easy", "medium", "hard"]
    cols  = ["blue", "red", "green", "white"]
    back  = pygame.Rect(W//2 - 80, 545, 160, 40)

    while True:
        DISPLAY.fill(DARK)
        panel(DISPLAY, 30, 70, W-60, 455)
        txt(DISPLAY, "SETTINGS", F_MID, ACCENT, W//2, 45)

        # Sound
        txt(DISPLAY, "Sound:", F_SM, WHITE, 130, 115)
        sv = pygame.Rect(230, 100, 120, 34)
        sc = GREEN if cfg["sound"] else RED
        button(DISPLAY, sv, "ON" if cfg["sound"] else "OFF", F_SM, False)
        pygame.draw.rect(DISPLAY, sc, sv, 2, border_radius=8)

        # Difficulty
        txt(DISPLAY, "Difficulty:", F_SM, WHITE, 115, 175)
        pd = pygame.Rect(200, 160, 30, 34)
        nd = pygame.Rect(340, 160, 30, 34)
        button(DISPLAY, pd, "<", F_SM)
        button(DISPLAY, nd, ">", F_SM)
        txt(DISPLAY, cfg["difficulty"].capitalize(), F_SM, ACCENT, 285, 177)

        # Car color
        txt(DISPLAY, "Car Color:", F_SM, WHITE, 115, 235)
        pc = pygame.Rect(200, 220, 30, 34)
        nc = pygame.Rect(340, 220, 30, 34)
        button(DISPLAY, pc, "<", F_SM)
        button(DISPLAY, nc, ">", F_SM)
        sw = pygame.Surface((60, 28))
        sw.fill(CAR_TINTS[cfg["car_color"]])
        DISPLAY.blit(sw, sw.get_rect(center=(285, 237)))
        pygame.draw.rect(DISPLAY, ACCENT, sw.get_rect(center=(285, 237)), 2)

        button(DISPLAY, back, "SAVE & BACK", F_SM)
        pygame.display.update()
        clock.tick(FPS)

        di = diffs.index(cfg["difficulty"])
        ci = cols.index(cfg["car_color"])

        for e in pygame.event.get():
            if e.type == QUIT: pygame.quit(); sys.exit()
            if btn_clicked(e, sv): cfg["sound"] = not cfg["sound"]
            if btn_clicked(e, pd): cfg["difficulty"] = diffs[(di-1) % 3]
            if btn_clicked(e, nd): cfg["difficulty"] = diffs[(di+1) % 3]
            if btn_clicked(e, pc): cfg["car_color"]  = cols[(ci-1) % 4]
            if btn_clicked(e, nc): cfg["car_color"]  = cols[(ci+1) % 4]
            if btn_clicked(e, back): save_settings(cfg); return


# ══════════════════════════════════════════════════════════════════════════════
#  Game-over screen
# ══════════════════════════════════════════════════════════════════════════════

def game_over_screen(score: int, coins: int, dist: int, name: str, hp: int = 0) -> str:
    """Shows results, saves the score. Returns 'retry' or 'menu'."""
    save_score(name, score, dist, coins, hp)

    retry = pygame.Rect(W//2 - 115, 450, 100, 40)
    menu  = pygame.Rect(W//2 +  15, 450, 100, 40)

    while True:
        DISPLAY.fill(DARK)
        panel(DISPLAY, 40, 90, W-80, 340)

        txt(DISPLAY, "GAME OVER", F_BIG, RED, W//2, 55)

        hp_col = GREEN if hp >= 2 else (GOLD if hp == 1 else RED)
        for i, (k, v, c) in enumerate([
            ("Player",   name,        WHITE),
            ("Score",    str(score),  GOLD),
            ("Coins",    str(coins),  GOLD),
            ("Distance", f"{dist}m",  GRAY),
            ("HP left",  str(hp),     hp_col),
        ]):
            ks = F_SM.render(k + ":", True, GRAY)
            vs = F_SM.render(v,       True, c)
            DISPLAY.blit(ks, (70, 112 + i*46))
            DISPLAY.blit(vs, (W - 70 - vs.get_width(), 112 + i*46))

        button(DISPLAY, retry, "RETRY", F_SM)
        button(DISPLAY, menu,  "MENU",  F_SM)
        pygame.display.update()
        clock.tick(FPS)

        for e in pygame.event.get():
            if e.type == QUIT: pygame.quit(); sys.exit()
            if btn_clicked(e, retry): return "retry"
            if btn_clicked(e, menu):  return "menu"
