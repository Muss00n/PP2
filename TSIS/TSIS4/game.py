"""
game.py – core Snake gameplay (one round).

Called from main.py with context already set up.
Returns  'gameover'  when the round ends.
"""
import pygame
import random
import time

import config
import db
import settings as settings_mod


# ── Helpers ───────────────────────────────────────────────────────────────────

def _grid(val: int) -> int:
    """Snap a pixel value to the nearest grid cell."""
    return (val // config.GRID) * config.GRID


def _rand_cell(exclude: list[list] | None = None) -> list[int]:
    """Return a random free grid cell [x, y], avoiding cells in *exclude*."""
    exclude = exclude or []
    while True:
        x = random.randrange(1, config.WINDOW_W // config.GRID) * config.GRID
        y = random.randrange(1, config.WINDOW_H // config.GRID) * config.GRID
        if [x, y] not in exclude:
            return [x, y]


# ── Food ──────────────────────────────────────────────────────────────────────

def _spawn_food(occupied: list[list]) -> dict:
    weight, color, lifetime = random.choice(config.FOOD_TYPES)
    return {
        "pos":      _rand_cell(occupied),
        "weight":   weight,
        "color":    color,
        "spawn":    time.time(),
        "lifetime": lifetime,
        "type":     "normal",
    }


def _spawn_poison(occupied: list[list]) -> dict:
    return {
        "pos":      _rand_cell(occupied),
        "weight":   0,
        "color":    config.DARK_RED,
        "spawn":    time.time(),
        "lifetime": 6.0,
        "type":     "poison",
    }


# ── Power-ups ─────────────────────────────────────────────────────────────────

POWERUP_DEFS = [
    {"kind": "speed",   "color": config.CYAN,   "label": "FAST"},
    {"kind": "slow",    "color": config.PURPLE,  "label": "SLOW"},
    {"kind": "shield",  "color": config.GOLD,    "label": "SHIELD"},
]


def _spawn_powerup(occupied: list[list]) -> dict:
    defn = random.choice(POWERUP_DEFS)
    return {
        "pos":        _rand_cell(occupied),
        "kind":       defn["kind"],
        "color":      defn["color"],
        "label":      defn["label"],
        "field_tick": pygame.time.get_ticks(),  # when it appeared on the field
    }


# ── Obstacles ─────────────────────────────────────────────────────────────────

def _place_obstacles(existing_obstacles: list[list], snake_body: list[list],
                     foods: list[dict], count: int) -> list[list]:
    """Add *count* new obstacle cells that don't trap the snake head."""
    occupied = existing_obstacles + snake_body + [f["pos"] for f in foods]
    new_blocks = []
    attempts = 0
    while len(new_blocks) < count and attempts < 500:
        attempts += 1
        cell = _rand_cell(occupied + new_blocks)
        # Simple safety check: cell must not be adjacent to the snake head
        hx, hy = snake_body[0]
        if abs(cell[0] - hx) <= config.GRID * 3 and abs(cell[1] - hy) <= config.GRID * 3:
            continue
        new_blocks.append(cell)
    return existing_obstacles + new_blocks


# ── Main game function ────────────────────────────────────────────────────────

def run_game(surface: pygame.Surface, clock: pygame.time.Clock,
             username: str, player_id: int | None,
             personal_best: int, user_settings: dict) -> tuple[str, int, int]:
    """
    Play one full round.

    Returns (next_state, final_score, level_reached).
    next_state is 'gameover'.
    """
    snake_color = tuple(user_settings.get("snake_color", config.GREEN))
    grid_on     = user_settings.get("grid_overlay", False)

    # ── State ──────────────────────────────────────────────────────────────
    snake_pos   = [100, 50]
    snake_body  = [[100, 50], [90, 50], [80, 50], [70, 50]]
    direction   = "RIGHT"
    change_to   = "RIGHT"
    score       = 0
    level       = 1
    speed       = config.FPS_BASE
    obstacles: list[list] = []

    # Power-up must be defined before occupied_cells() is called
    powerup: dict | None = None
    powerup_spawn_tick = 0

    def occupied_cells():
        return snake_body + obstacles + [f["pos"] for f in foods] + (
            [powerup["pos"]] if powerup else []
        )

    # Foods
    foods: list[dict] = []
    for _ in range(config.MAX_FOODS):
        foods.append(_spawn_food(snake_body))
    # One poison food
    poison: dict | None = _spawn_poison(occupied_cells())
    POWERUP_INTERVAL = 10_000  # try to spawn one every ~10 s

    # Active effects
    active_effect: str | None = None  # 'speed' | 'slow' | None
    effect_end_tick = 0
    shield_active   = False

    # Fonts
    font_sm = pygame.font.SysFont("consolas", 18)
    font_md = pygame.font.SysFont("consolas", 26)

    def show_hud():
        # Score
        surface.blit(font_sm.render(f"Score: {score}", True, config.WHITE), (4, 2))
        surface.blit(font_sm.render(f"Level: {level}", True, config.YELLOW), (4, 22))
        surface.blit(font_sm.render(f"Best:  {personal_best}", True, config.LIGHT_GREY), (4, 42))
        surface.blit(font_sm.render(f"User:  {username}", True, config.LIGHT_GREY), (4, 62))

        # Active effect banner
        if active_effect:
            remaining = max(0, (effect_end_tick - pygame.time.get_ticks()) // 1000)
            text = f"{'⚡ FAST' if active_effect == 'speed' else '🐢 SLOW'}  {remaining}s"
            surf = font_sm.render(text, True, config.CYAN if active_effect == "speed" else config.PURPLE)
            surface.blit(surf, (config.WINDOW_W // 2 - surf.get_width() // 2, 4))
        if shield_active:
            surf = font_sm.render("🛡 SHIELD", True, config.GOLD)
            surface.blit(surf, (config.WINDOW_W // 2 - surf.get_width() // 2, 24))

        # Food legend (top-right)
        lx, ly = config.WINDOW_W - 160, 4
        for weight, color, lt in config.FOOD_TYPES:
            pygame.draw.rect(surface, color, (lx, ly, 10, 10))
            surface.blit(font_sm.render(f"= {weight}pts ({lt}s)", True, config.WHITE), (lx + 14, ly - 1))
            ly += 18

    running = True
    while running:
        now_ticks = pygame.time.get_ticks()
        now_time  = time.time()

        # ── Events ────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:    change_to = "UP"
                if event.key == pygame.K_DOWN:  change_to = "DOWN"
                if event.key == pygame.K_LEFT:  change_to = "LEFT"
                if event.key == pygame.K_RIGHT: change_to = "RIGHT"
                if event.key == pygame.K_ESCAPE:
                    return "gameover", score, level

        # ── Direction ─────────────────────────────────────────────────────
        if change_to == "UP"    and direction != "DOWN":  direction = "UP"
        if change_to == "DOWN"  and direction != "UP":    direction = "DOWN"
        if change_to == "LEFT"  and direction != "RIGHT": direction = "LEFT"
        if change_to == "RIGHT" and direction != "LEFT":  direction = "RIGHT"

        # ── Move ──────────────────────────────────────────────────────────
        if direction == "UP":    snake_pos[1] -= config.GRID
        if direction == "DOWN":  snake_pos[1] += config.GRID
        if direction == "LEFT":  snake_pos[0] -= config.GRID
        if direction == "RIGHT": snake_pos[0] += config.GRID

        snake_body.insert(0, list(snake_pos))

        # ── Eat food? ─────────────────────────────────────────────────────
        ate = False
        for food in foods[:]:
            if snake_pos == food["pos"]:
                score += food["weight"]
                foods.remove(food)
                foods.append(_spawn_food(occupied_cells()))

                # Level-up
                new_level = (score // config.POINTS_PER_LEVEL) + 1
                if new_level > level:
                    level = new_level
                    speed += config.SPEED_INCREMENT
                    if level >= config.OBSTACLES_START_LEVEL:
                        obstacles = _place_obstacles(
                            obstacles, snake_body, foods,
                            config.OBSTACLE_COUNT_PER_LEVEL
                        )
                ate = True
                break

        # ── Eat poison? ───────────────────────────────────────────────────
        if poison and snake_pos == poison["pos"]:
            snake_body = snake_body[:-2] if len(snake_body) > 2 else snake_body[:1]
            poison = _spawn_poison(occupied_cells())
            if len(snake_body) <= 1:
                running = False

        # ── Eat power-up? ─────────────────────────────────────────────────
        if powerup and snake_pos == powerup["pos"]:
            kind = powerup["kind"]
            if kind == "speed":
                active_effect  = "speed"
                effect_end_tick = now_ticks + config.POWERUP_EFFECT_DURATION
                speed = max(5, min(config.FPS_BASE + config.SPEED_BOOST_DELTA + (level - 1) * config.SPEED_INCREMENT, 60))
            elif kind == "slow":
                active_effect  = "slow"
                effect_end_tick = now_ticks + config.POWERUP_EFFECT_DURATION
                speed = max(5, speed + config.SLOW_MOTION_DELTA)
            elif kind == "shield":
                shield_active = True
            powerup = None
            powerup_spawn_tick = now_ticks  # reset interval

        if not ate:
            snake_body.pop()

        # ── Expire effects ────────────────────────────────────────────────
        if active_effect and now_ticks >= effect_end_tick:
            active_effect = None
            # Recalculate base speed
            speed = config.FPS_BASE + (level - 1) * config.SPEED_INCREMENT

        # ── Expire food ───────────────────────────────────────────────────
        for food in foods[:]:
            if now_time - food["spawn"] >= food["lifetime"]:
                foods.remove(food)
                foods.append(_spawn_food(occupied_cells()))

        # ── Expire poison ─────────────────────────────────────────────────
        if poison and now_time - poison["spawn"] >= poison["lifetime"]:
            poison = _spawn_poison(occupied_cells())

        # ── Manage power-ups ──────────────────────────────────────────────
        if powerup is None:
            if now_ticks - powerup_spawn_tick >= POWERUP_INTERVAL:
                powerup = _spawn_powerup(occupied_cells())
                powerup_spawn_tick = now_ticks
        else:
            if now_ticks - powerup["field_tick"] >= config.POWERUP_FIELD_LIFETIME:
                powerup = None
                powerup_spawn_tick = now_ticks

        # ── Maintain MAX_FOODS ────────────────────────────────────────────
        while len(foods) < config.MAX_FOODS:
            foods.append(_spawn_food(occupied_cells()))

        # ── Collision detection ───────────────────────────────────────────
        # Wall
        hit_wall = (
            snake_pos[0] < 0 or snake_pos[0] >= config.WINDOW_W or
            snake_pos[1] < 0 or snake_pos[1] >= config.WINDOW_H
        )
        # Self
        hit_self = snake_pos in snake_body[1:]
        # Obstacle
        hit_obstacle = snake_pos in obstacles

        if hit_wall or hit_self or hit_obstacle:
            if shield_active:
                shield_active = False
                # Bounce back: reverse head to previous body segment
                snake_pos[0] = snake_body[1][0]
                snake_pos[1] = snake_body[1][1]
                snake_body[0] = list(snake_pos)
            else:
                running = False

        # ── Draw ──────────────────────────────────────────────────────────
        surface.fill(config.BLACK)

        # Grid overlay
        if grid_on:
            for gx in range(0, config.WINDOW_W, config.GRID):
                pygame.draw.line(surface, (30, 30, 30), (gx, 0), (gx, config.WINDOW_H))
            for gy in range(0, config.WINDOW_H, config.GRID):
                pygame.draw.line(surface, (30, 30, 30), (0, gy), (config.WINDOW_W, gy))

        # Obstacles
        for cell in obstacles:
            pygame.draw.rect(surface, config.DARK_GREY,
                             pygame.Rect(cell[0], cell[1], config.GRID, config.GRID))

        # Snake
        for i, seg in enumerate(snake_body):
            color = snake_color if i > 0 else config.WHITE
            pygame.draw.rect(surface, color,
                             pygame.Rect(seg[0], seg[1], config.GRID, config.GRID))

        # Normal foods
        for food in foods:
            elapsed  = now_time - food["spawn"]
            fraction = max(0.0, 1.0 - elapsed / food["lifetime"])
            if fraction < 0.25 and int(now_time * 6) % 2 == 0:
                pass  # blinking – skip this frame
            else:
                pygame.draw.rect(surface, food["color"],
                                 pygame.Rect(food["pos"][0], food["pos"][1],
                                             config.GRID, config.GRID))
            # Timer bar
            bx, by = food["pos"][0] - 10, food["pos"][1] - 6
            pygame.draw.rect(surface, config.WHITE, (bx, by, 30, 3))
            pygame.draw.rect(surface, food["color"], (bx, by, int(30 * fraction), 3))

        # Poison food
        if poison:
            e = now_time - poison["spawn"]
            fr = max(0.0, 1.0 - e / poison["lifetime"])
            if fr >= 0.25 or int(now_time * 6) % 2 == 0:
                pygame.draw.rect(surface, config.DARK_RED,
                                 pygame.Rect(poison["pos"][0], poison["pos"][1],
                                             config.GRID, config.GRID))
                # X mark
                px, py = poison["pos"]
                pygame.draw.line(surface, config.WHITE,
                                 (px, py), (px + config.GRID, py + config.GRID), 2)
                pygame.draw.line(surface, config.WHITE,
                                 (px + config.GRID, py), (px, py + config.GRID), 2)

        # Power-up
        if powerup:
            px, py = powerup["pos"]
            pygame.draw.rect(surface, powerup["color"],
                             pygame.Rect(px, py, config.GRID * 2, config.GRID * 2))
            lbl = font_sm.render(powerup["label"], True, config.BLACK)
            surface.blit(lbl, (px + 1, py + 1))

        show_hud()
        pygame.display.update()
        clock.tick(speed)

    # ── Round finished ────────────────────────────────────────────────────────
    return "gameover", score, level