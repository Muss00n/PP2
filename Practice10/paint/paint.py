import pygame
import math

def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("Drawing App")
    clock = pygame.time.Clock()

    radius = 15
    mode = 'blue'
    # All available tools
    tool = 'draw'
    points = []

    # Stores the starting point when dragging shapes
    shape_start = None

    # Canvas surface where all finished drawings are saved
    canvas = pygame.Surface((640, 480))
    canvas.fill((0, 0, 0))

    # --- Color palette swatches ---
    palette_colors = [
        (255, 0,   0),
        (0,   255, 0),
        (0,   0,   255),
        (255, 255, 0),
        (255, 165, 0),
        (128, 0,   128),
        (255, 255, 255),
        (128, 128, 128),
    ]
    custom_color = palette_colors[2]  # Default: blue

    SWATCH = 30
    palette_rects = []
    for i, col in enumerate(palette_colors):
        palette_rects.append(pygame.Rect(10 + i * (SWATCH + 5), 440, SWATCH, SWATCH))

    # --- Tool buttons at the top ---
    font = pygame.font.SysFont("Verdana", 12)

    # All tools including the new shapes
    tools = ['draw', 'rectangle', 'circle', 'eraser',
             'square', 'right_tri', 'eq_tri', 'rhombus']

    # Labels shown on the buttons (shorter text to fit)
    tool_labels = ['1:Draw', '2:Rect', '3:Circle', '4:Eraser',
                   '5:Square', '6:R.Tri', '7:Eq.Tri', '8:Rhombus']

    tool_rects = []
    for i in range(len(tools)):
        # Two rows of buttons: first 4 on top, next 4 below
        row = i // 4
        col = i % 4
        tool_rects.append(pygame.Rect(10 + col * 110, 5 + row * 32, 100, 26))

    def get_color():
        """Return the current drawing color as an RGB tuple."""
        if mode == 'custom':
            return custom_color
        elif mode == 'red':
            return (220, 50, 50)
        elif mode == 'green':
            return (50, 220, 50)
        else:
            return (50, 50, 220)

    def draw_shape(surface, tool, start, end, color):
        """
        Draw a completed shape onto the given surface.
        start and end are (x, y) tuples from mouse press and release.
        """
        x0, y0 = start
        x1, y1 = end

        if tool == 'rectangle':
            # Axis-aligned rectangle from start to end
            rect = pygame.Rect(min(x0,x1), min(y0,y1), abs(x1-x0), abs(y1-y0))
            pygame.draw.rect(surface, color, rect, 2)

        elif tool == 'square':
            # Force equal width and height using the smaller dimension
            side = min(abs(x1-x0), abs(y1-y0))
            # Preserve direction of drag
            sx = side if x1 > x0 else -side
            sy = side if y1 > y0 else -side
            rect = pygame.Rect(min(x0, x0+sx), min(y0, y0+sy), side, side)
            pygame.draw.rect(surface, color, rect, 2)

        elif tool == 'circle':
            # Radius = distance between start and end points
            r = int(math.hypot(x1-x0, y1-y0))
            pygame.draw.circle(surface, color, start, r, 2)

        elif tool == 'right_tri':
            # Right angle at start point
            # Three vertices: start (right angle), below start, end point
            p1 = (x0, y0)        # right angle corner
            p2 = (x0, y1)        # directly below start
            p3 = (x1, y1)        # end point
            pygame.draw.polygon(surface, color, [p1, p2, p3], 2)

        elif tool == 'eq_tri':
            # Equilateral triangle: base from start to end, third point above center
            # Base midpoint
            mx = (x0 + x1) / 2
            my = (y0 + y1) / 2
            # Base length
            base = math.hypot(x1-x0, y1-y0)
            # Height of equilateral triangle
            h = base * math.sqrt(3) / 2
            # Angle of the base line
            angle = math.atan2(y1-y0, x1-x0)
            # Third point is perpendicular to the base, offset by height
            p3x = mx - h * math.sin(angle)
            p3y = my + h * math.cos(angle)
            pygame.draw.polygon(surface, color, [(x0,y0), (x1,y1), (int(p3x), int(p3y))], 2)

        elif tool == 'rhombus':
            # Rhombus (diamond) using start as center, end defining width/height
            cx, cy = x0, y0
            hw = abs(x1 - x0)   # half-width
            hh = abs(y1 - y0)   # half-height
            # Four points: top, right, bottom, left
            points_shape = [
                (cx,      cy - hh),   # top
                (cx + hw, cy),        # right
                (cx,      cy + hh),   # bottom
                (cx - hw, cy),        # left
            ]
            pygame.draw.polygon(surface, color, points_shape, 2)

    # --- Main loop ---
    while True:

        pressed = pygame.key.get_pressed()
        alt_held  = pressed[pygame.K_LALT]  or pressed[pygame.K_RALT]
        ctrl_held = pressed[pygame.K_LCTRL] or pressed[pygame.K_RCTRL]
        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()

        for event in pygame.event.get():

            # --- Quit conditions ---
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_w and ctrl_held) or \
                   (event.key == pygame.K_F4 and alt_held) or \
                    event.key == pygame.K_ESCAPE:
                    return

                # Keyboard shortcuts for color
                if event.key == pygame.K_r:   mode = 'red'
                elif event.key == pygame.K_g: mode = 'green'
                elif event.key == pygame.K_b: mode = 'blue'

                # Keyboard shortcuts for tools (1-8)
                if event.key == pygame.K_1:   tool = 'draw'
                elif event.key == pygame.K_2: tool = 'rectangle'
                elif event.key == pygame.K_3: tool = 'circle'
                elif event.key == pygame.K_4: tool = 'eraser'
                elif event.key == pygame.K_5: tool = 'square'
                elif event.key == pygame.K_6: tool = 'right_tri'
                elif event.key == pygame.K_7: tool = 'eq_tri'
                elif event.key == pygame.K_8: tool = 'rhombus'

                # C key clears the canvas
                if event.key == pygame.K_c:
                    canvas.fill((0, 0, 0))
                    points = []

            # --- Mouse wheel: resize brush ---
            if event.type == pygame.MOUSEWHEEL:
                radius = max(1, min(200, radius + event.y))

            # --- Mouse button down ---
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Check if a tool button was clicked
                for i, rect in enumerate(tool_rects):
                    if rect.collidepoint(event.pos):
                        tool = tools[i]
                        break

                # Check if a palette swatch was clicked
                for i, rect in enumerate(palette_rects):
                    if rect.collidepoint(event.pos):
                        custom_color = palette_colors[i]
                        mode = 'custom'
                        break

                # Record start position for shape tools
                if tool in ('rectangle', 'circle', 'square',
                            'right_tri', 'eq_tri', 'rhombus'):
                    shape_start = event.pos

            # --- Mouse button up: commit shape to canvas ---
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if shape_start and tool in ('rectangle', 'circle', 'square',
                                            'right_tri', 'eq_tri', 'rhombus'):
                    draw_shape(canvas, tool, shape_start, event.pos, get_color())
                    shape_start = None

            # --- Mouse motion: freehand draw or eraser ---
            if event.type == pygame.MOUSEMOTION:
                if tool == 'draw' and mouse_buttons[0]:
                    points.append(event.pos)
                    # Draw immediately onto canvas as the mouse moves
                    if len(points) >= 2:
                        drawLineBetween(canvas, 200, points[-2], points[-1], radius, mode, custom_color)
                elif tool == 'eraser' and mouse_buttons[0]:
                    pygame.draw.circle(canvas, (0, 0, 0), event.pos, radius)

            # Clear points when mouse released so next stroke starts fresh
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if tool == 'draw':
                    points = []

        # --- Compose frame ---
        screen.blit(canvas, (0, 0))

        # Live preview while dragging a shape (drawn on screen, not canvas)
        if shape_start and mouse_buttons[0]:
            draw_shape(screen, tool, shape_start, mouse_pos, get_color())

        # Eraser cursor outline
        if tool == 'eraser':
            pygame.draw.circle(screen, (200, 200, 200), mouse_pos, radius, 2)

        # --- UI: top bar ---
        pygame.draw.rect(screen, (30, 30, 30), (0, 0, 640, 70))
        for i, (t, rect, label) in enumerate(zip(tools, tool_rects, tool_labels)):
            btn_color = (80, 80, 200) if t == tool else (60, 60, 60)
            pygame.draw.rect(screen, btn_color, rect, border_radius=4)
            pygame.draw.rect(screen, (150, 150, 150), rect, 1, border_radius=4)
            txt = font.render(label, True, (255, 255, 255))
            screen.blit(txt, (rect.x + 4, rect.y + 7))

        # --- UI: bottom bar ---
        pygame.draw.rect(screen, (30, 30, 30), (0, 432, 640, 48))
        for col, rect in zip(palette_colors, palette_rects):
            pygame.draw.rect(screen, col, rect, border_radius=4)
            if mode == 'custom' and custom_color == col:
                pygame.draw.rect(screen, (255, 255, 255), rect, 2, border_radius=4)

        # Current color preview box
        pygame.draw.rect(screen, get_color(), pygame.Rect(300, 440, SWATCH, SWATCH), border_radius=4)
        hint = font.render(f"Brush:{radius}  Scroll=resize  C=clear  R/G/B=color", True, (180, 180, 180))
        screen.blit(hint, (340, 448))

        pygame.display.flip()
        clock.tick(60)


def drawLineBetween(surface, index, start, end, width, color_mode, custom_color):
    """
    Draw a smooth brush stroke between two points by placing circles along the path.
    Color fades based on index to create a gradient trail effect.
    """
    c1 = max(0, min(255, 2 * index - 256))
    c2 = max(0, min(255, 2 * index))

    if color_mode == 'blue':
        color = (c1, c1, c2)
    elif color_mode == 'red':
        color = (c2, c1, c1)
    elif color_mode == 'green':
        color = (c1, c2, c1)
    else:
        color = custom_color  # Solid color from palette

    dx = start[0] - end[0]
    dy = start[1] - end[1]
    iterations = max(abs(dx), abs(dy))

    for i in range(iterations):
        progress = 1.0 * i / iterations
        aprogress = 1 - progress
        x = int(aprogress * start[0] + progress * end[0])
        y = int(aprogress * start[1] + progress * end[1])
        pygame.draw.circle(surface, color, (x, y), width)


main()