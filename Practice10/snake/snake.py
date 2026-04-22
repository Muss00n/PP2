# importing libraries
import pygame
import time
import random

snake_speed = 15

# Window size
window_x = 720
window_y = 480

# defining colors
black  = pygame.Color(0,   0,   0)
white  = pygame.Color(255, 255, 255)
red    = pygame.Color(255, 0,   0)
green  = pygame.Color(0,   255, 0)
blue   = pygame.Color(0,   0,   255)
yellow = pygame.Color(255, 255, 0)
orange = pygame.Color(255, 165, 0)

# Initialising pygame
pygame.init()

# Initialise game window
pygame.display.set_caption('Snake')
game_window = pygame.display.set_mode((window_x, window_y))

# FPS controller
fps = pygame.time.Clock()

# Snake starting position
snake_position = [100, 50]

# Snake body: first 4 blocks
snake_body = [
    [100, 50],
    [90,  50],
    [80,  50],
    [70,  50],
]

# --- Food system ---
# Each food item is a dict:
#   'pos'     : [x, y]         – position on grid
#   'weight'  : int            – points awarded when eaten
#   'color'   : pygame.Color   – visual color based on weight
#   'spawn'   : float          – time.time() when it was created
#   'lifetime': float          – seconds before it disappears

# Food weight types: (weight, color, lifetime_seconds)
FOOD_TYPES = [
    (5,  white,  8.0),   # common  – lasts 8 s
    (10, yellow, 6.0),   # uncommon – lasts 6 s
    (20, orange, 4.0),   # rare    – lasts 4 s
    (50, red,    2.5),   # epic    – lasts 2.5 s
]

def spawn_food():
    """Create a new food item at a random grid position with a random type."""
    weight, color, lifetime = random.choice(FOOD_TYPES)
    pos = [
        random.randrange(1, (window_x // 10)) * 10,
        random.randrange(1, (window_y // 10)) * 10,
    ]
    return {
        'pos':      pos,
        'weight':   weight,
        'color':    color,
        'spawn':    time.time(),
        'lifetime': lifetime,
    }

# Start with two food items on the board
foods = [spawn_food(), spawn_food()]

# How many food items should always be on the board
MAX_FOODS = 3

# Snake direction
direction = 'RIGHT'
change_to  = direction

# Score and level
score = 0
level = 1
points_per_level = 50   # points needed to advance one level

# ── UI helpers ────────────────────────────────────────────────────────────────

def show_score(color, font, size):
    """Render the current score in the top-left corner."""
    score_font    = pygame.font.SysFont(font, size)
    score_surface = score_font.render('Score : ' + str(score), True, color)
    game_window.blit(score_surface, (0, 0))

def show_level(color, font, size):
    """Render the current level just below the score."""
    level_font    = pygame.font.SysFont(font, size)
    level_surface = level_font.render('Level : ' + str(level), True, color)
    game_window.blit(level_surface, (0, 22))

def show_food_legend(font_obj):
    """
    Draw a small legend in the top-right corner showing
    each food color and its point value.
    """
    x_start = window_x - 150
    y_start = 5
    for weight, color, lifetime in FOOD_TYPES:
        pygame.draw.rect(game_window, color, (x_start, y_start, 10, 10))
        label = font_obj.render(f'= {weight} pts  ({lifetime}s)', True, white)
        game_window.blit(label, (x_start + 14, y_start - 1))
        y_start += 16

def game_over():
    """Display the final score and quit after 2 seconds."""
    my_font = pygame.font.SysFont('times new roman', 50)
    game_over_surface = my_font.render('Your Score is : ' + str(score), True, red)
    game_over_rect    = game_over_surface.get_rect()
    game_over_rect.midtop = (window_x / 2, window_y / 4)
    game_window.blit(game_over_surface, game_over_rect)
    pygame.display.flip()
    time.sleep(2)
    pygame.quit()
    quit()

# Small font for the legend
legend_font = pygame.font.SysFont('times new roman', 14)

# ── Main loop ─────────────────────────────────────────────────────────────────
while True:

    # Handle key events
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:    change_to = 'UP'
            if event.key == pygame.K_DOWN:  change_to = 'DOWN'
            if event.key == pygame.K_LEFT:  change_to = 'LEFT'
            if event.key == pygame.K_RIGHT: change_to = 'RIGHT'

    # Prevent reversing direction
    if change_to == 'UP'    and direction != 'DOWN':  direction = 'UP'
    if change_to == 'DOWN'  and direction != 'UP':    direction = 'DOWN'
    if change_to == 'LEFT'  and direction != 'RIGHT': direction = 'LEFT'
    if change_to == 'RIGHT' and direction != 'LEFT':  direction = 'RIGHT'

    # Move snake head one block in the current direction
    if direction == 'UP':    snake_position[1] -= 10
    if direction == 'DOWN':  snake_position[1] += 10
    if direction == 'LEFT':  snake_position[0] -= 10
    if direction == 'RIGHT': snake_position[0] += 10

    # Grow snake: prepend new head position
    snake_body.insert(0, list(snake_position))

    # --- Check if snake eats any food ---
    ate = False
    for food in foods[:]:           # iterate over a copy so we can remove safely
        if snake_position[0] == food['pos'][0] and snake_position[1] == food['pos'][1]:
            score += food['weight']     # add food's weight to score
            foods.remove(food)          # remove eaten food
            foods.append(spawn_food())  # immediately replace with a new one

            # Level-up check
            new_level = (score // points_per_level) + 1
            if new_level > level:
                level      = new_level
                snake_speed += 3        # get faster each level

            ate = True
            break

    # If nothing was eaten, remove the tail (normal movement)
    if not ate:
        snake_body.pop()

    # --- Expire foods whose lifetime has run out ---
    now = time.time()
    for food in foods[:]:
        if now - food['spawn'] >= food['lifetime']:
            foods.remove(food)          # disappear
            foods.append(spawn_food())  # replace with a fresh one

    # --- Keep the board topped up to MAX_FOODS ---
    while len(foods) < MAX_FOODS:
        foods.append(spawn_food())

    # ── Draw everything ───────────────────────────────────────────────────────
    game_window.fill(black)

    # Draw snake body
    for pos in snake_body:
        pygame.draw.rect(game_window, green, pygame.Rect(pos[0], pos[1], 10, 10))

    # Draw each food item
    for food in foods:
        # Calculate how much lifetime remains (0.0 – 1.0)
        elapsed  = now - food['spawn']
        fraction = 1.0 - (elapsed / food['lifetime'])   # 1 = fresh, 0 = about to vanish

        # Blink fast when less than 25 % of lifetime remains
        if fraction < 0.25:
            # Toggle visibility on/off rapidly using current time
            if int(now * 6) % 2 == 0:
                pygame.draw.rect(game_window, food['color'],
                                 pygame.Rect(food['pos'][0], food['pos'][1], 10, 10))
        else:
            pygame.draw.rect(game_window, food['color'],
                             pygame.Rect(food['pos'][0], food['pos'][1], 10, 10))

        # Timer bar above each food (shrinks as time runs out)
        bar_width = int(30 * fraction)
        bar_x     = food['pos'][0] - 10
        bar_y     = food['pos'][1] - 6
        pygame.draw.rect(game_window, white, (bar_x, bar_y, 30, 3))        # background
        pygame.draw.rect(game_window, food['color'], (bar_x, bar_y, bar_width, 3))  # fill

    # Game-over conditions: hit a wall
    if snake_position[0] < 0 or snake_position[0] > window_x - 10:
        game_over()
    if snake_position[1] < 0 or snake_position[1] > window_y - 10:
        game_over()

    # Game-over condition: snake bites itself
    for block in snake_body[1:]:
        if snake_position[0] == block[0] and snake_position[1] == block[1]:
            game_over()

    # HUD
    show_score(white,  'times new roman', 20)
    show_level(yellow, 'times new roman', 20)
    show_food_legend(legend_font)

    pygame.display.update()
    fps.tick(snake_speed)