# ── Window ────────────────────────────────────────────────────────────────────
WINDOW_W = 720
WINDOW_H = 480
GRID     = 10          # size of one cell in pixels
FPS_BASE = 15          # starting FPS / snake speed

# ── Colours (R, G, B) ─────────────────────────────────────────────────────────
BLACK       = (0,   0,   0)
WHITE       = (255, 255, 255)
RED         = (255,   0,   0)
GREEN       = (0,   200,   0)
BLUE        = (0,     0, 255)
YELLOW      = (255, 255,   0)
ORANGE      = (255, 165,   0)
DARK_RED    = (139,   0,   0)   # poison food
CYAN        = (0,   255, 255)   # speed-boost power-up
PURPLE      = (160,  32, 240)   # slow-motion power-up
GOLD        = (255, 215,   0)   # shield power-up
DARK_GREY   = (80,   80,  80)   # obstacle blocks
LIGHT_GREY  = (180, 180, 180)

# ── Food types: (weight, color, lifetime_seconds) ─────────────────────────────
FOOD_TYPES = [
    (5,  WHITE,  8.0),
    (10, YELLOW, 6.0),
    (20, ORANGE, 4.0),
    (50, RED,    2.5),
]

# ── Scoring / levelling ───────────────────────────────────────────────────────
POINTS_PER_LEVEL = 50
SPEED_INCREMENT  = 3
MAX_FOODS        = 3

# ── Power-up settings ─────────────────────────────────────────────────────────
POWERUP_FIELD_LIFETIME = 8_000   # ms before it vanishes from the field
POWERUP_EFFECT_DURATION = 5_000  # ms that speed/slow effect lasts
SPEED_BOOST_DELTA =  5           # FPS added
SLOW_MOTION_DELTA = -5           # FPS removed

# ── Obstacles ─────────────────────────────────────────────────────────────────
OBSTACLE_COUNT_PER_LEVEL = 4     # blocks added each time a new level spawns them
OBSTACLES_START_LEVEL    = 3
