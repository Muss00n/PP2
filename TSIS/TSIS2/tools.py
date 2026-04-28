import pygame
import math
import datetime


def flood_fill(surface, x, y, fill_color):
    """Iterative flood fill using a stack."""
    w, h = surface.get_size()
    if x < 0 or x >= w or y < 0 or y >= h:
        return
    target_color = surface.get_at((x, y))[:3]
    fill_rgb = fill_color[:3]
    if target_color == fill_rgb:
        return

    stack = [(x, y)]
    visited = set()
    while stack:
        cx, cy = stack.pop()
        if (cx, cy) in visited:
            continue
        if cx < 0 or cx >= w or cy < 0 or cy >= h:
            continue
        current = surface.get_at((cx, cy))[:3]
        if current != target_color:
            continue
        visited.add((cx, cy))
        surface.set_at((cx, cy), fill_rgb)
        stack.append((cx + 1, cy))
        stack.append((cx - 1, cy))
        stack.append((cx, cy + 1))
        stack.append((cx, cy - 1))


def draw_shape(surface, tool, start, end, color, brush_size):
    """Draw a finished shape onto a surface."""
    x0, y0 = start
    x1, y1 = end

    if tool == 'rectangle':
        rect = pygame.Rect(min(x0, x1), min(y0, y1), abs(x1 - x0), abs(y1 - y0))
        pygame.draw.rect(surface, color, rect, brush_size)

    elif tool == 'square':
        side = min(abs(x1 - x0), abs(y1 - y0))
        sx = side if x1 > x0 else -side
        sy = side if y1 > y0 else -side
        rect = pygame.Rect(min(x0, x0 + sx), min(y0, y0 + sy), side, side)
        pygame.draw.rect(surface, color, rect, brush_size)

    elif tool == 'circle':
        r = int(math.hypot(x1 - x0, y1 - y0))
        if r > 0:
            pygame.draw.circle(surface, color, start, r, brush_size)

    elif tool == 'line':
        pygame.draw.line(surface, color, start, end, brush_size)

    elif tool == 'right_tri':
        p1 = (x0, y0)
        p2 = (x0, y1)
        p3 = (x1, y1)
        pygame.draw.polygon(surface, color, [p1, p2, p3], brush_size)

    elif tool == 'eq_tri':
        mx = (x0 + x1) / 2
        my = (y0 + y1) / 2
        base = math.hypot(x1 - x0, y1 - y0)
        h = base * math.sqrt(3) / 2
        angle = math.atan2(y1 - y0, x1 - x0)
        p3x = mx - h * math.sin(angle)
        p3y = my + h * math.cos(angle)
        pygame.draw.polygon(surface, color,
                            [(x0, y0), (x1, y1), (int(p3x), int(p3y))], brush_size)

    elif tool == 'rhombus':
        cx, cy = x0, y0
        hw = abs(x1 - x0)
        hh = abs(y1 - y0)
        pts = [(cx, cy - hh), (cx + hw, cy), (cx, cy + hh), (cx - hw, cy)]
        pygame.draw.polygon(surface, color, pts, brush_size)


def draw_pencil_segment(surface, p1, p2, width, color):
    """Draw a smooth freehand stroke segment between two points."""
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    iterations = max(abs(dx), abs(dy))
    if iterations == 0:
        pygame.draw.circle(surface, color, p1, width)
        return
    for i in range(iterations):
        progress = i / iterations
        aprogress = 1 - progress
        x = int(aprogress * p1[0] + progress * p2[0])
        y = int(aprogress * p1[1] + progress * p2[1])
        pygame.draw.circle(surface, color, (x, y), width)


def save_canvas(canvas):
    """Save the canvas surface as a timestamped PNG. Returns the filename."""
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"canvas_{ts}.png"
    pygame.image.save(canvas, fname)
    return fname


# Tools that use click-drag (start → end)
SHAPE_TOOLS = ('rectangle', 'circle', 'square',
               'right_tri', 'eq_tri', 'rhombus', 'line')

# All tool IDs in order
TOOLS = ['draw', 'line', 'rectangle', 'circle', 'eraser',
         'fill', 'text', 'square', 'right_tri', 'eq_tri', 'rhombus']

# Button labels matching TOOLS order
TOOL_LABELS = ['1:Pencil', '2:Line', '3:Rect', '4:Circle', '5:Eraser',
               '6:Fill', '7:Text', '8:Square', '9:R.Tri', '0:Eq.Tri', '-:Rhombus']

# Brush size options (px)
BRUSH_SIZES = [2, 5, 10]
BRUSH_LABELS = ['S(2px)', 'M(5px)', 'L(10px)']

# Default color palette swatches
PALETTE_COLORS = [
    (255, 0,   0),
    (0,   255, 0),
    (0,   0,   255),
    (255, 255, 0),
    (255, 165, 0),
    (128, 0,   128),
    (255, 255, 255),
    (128, 128, 128),
]