import pygame
from tools import (
    flood_fill, draw_shape, draw_pencil_segment, save_canvas,
    SHAPE_TOOLS, TOOLS, TOOL_LABELS,
    BRUSH_SIZES, BRUSH_LABELS,
    PALETTE_COLORS,
)


def main():
    pygame.init()

    W, H = 800, 560
    CANVAS_TOP  = 75   # pixels reserved for toolbar at top
    BOTTOM_BAR  = 48   # pixels reserved for palette bar at bottom
    CANVAS_H    = H - CANVAS_TOP - BOTTOM_BAR

    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Drawing App")
    clock = pygame.time.Clock()

    # ── Canvas ──────────────────────────────────────────────────────────────
    canvas = pygame.Surface((W, CANVAS_H))
    canvas.fill((0, 0, 0))

    # ── State ────────────────────────────────────────────────────────────────
    tool         = 'draw'
    brush_idx    = 1                       # default: medium (5 px)
    custom_color = PALETTE_COLORS[2]       # default: blue
    shape_start  = None                    # screen-space drag start
    points       = []                      # pencil stroke points

    # Text tool state
    text_active = False
    text_pos    = (0, 0)
    text_buffer = ""

    # ── Fonts ────────────────────────────────────────────────────────────────
    font      = pygame.font.SysFont("Verdana", 11)
    font_text = pygame.font.SysFont("Verdana", 20)

    # ── Build UI rects ───────────────────────────────────────────────────────
    BTN_W, BTN_H = 90, 24

    tool_rects = []
    for i in range(len(TOOLS)):
        row = i // 6
        col = i % 6
        tool_rects.append(pygame.Rect(8 + col * (BTN_W + 4), 4 + row * (BTN_H + 3), BTN_W, BTN_H))

    size_rects = []
    for i in range(len(BRUSH_SIZES)):
        size_rects.append(pygame.Rect(560 + i * 78, 4, 74, 24))

    SWATCH = 30
    PAL_Y  = H - BOTTOM_BAR + 9
    palette_rects = []
    for i in range(len(PALETTE_COLORS)):
        palette_rects.append(pygame.Rect(10 + i * (SWATCH + 5), PAL_Y, SWATCH, SWATCH))

    # ── Helpers ──────────────────────────────────────────────────────────────
    def get_color():
        return custom_color

    def to_canvas(screen_xy):
        return (screen_xy[0], screen_xy[1] - CANVAS_TOP)

    def on_canvas(screen_xy):
        return CANVAS_TOP <= screen_xy[1] < CANVAS_TOP + CANVAS_H

    # ── Main loop ────────────────────────────────────────────────────────────
    while True:
        pressed       = pygame.key.get_pressed()
        alt_held      = pressed[pygame.K_LALT]  or pressed[pygame.K_RALT]
        ctrl_held     = pressed[pygame.K_LCTRL] or pressed[pygame.K_RCTRL]
        mouse_pos     = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()
        brush         = BRUSH_SIZES[brush_idx]

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return

            if event.type == pygame.KEYDOWN:

                # Text tool captures all keys while active
                if text_active:
                    if event.key == pygame.K_RETURN:
                        surf = font_text.render(text_buffer, True, get_color())
                        canvas.blit(surf, to_canvas(text_pos))
                        text_active = False
                        text_buffer = ""
                    elif event.key == pygame.K_ESCAPE:
                        text_active = False
                        text_buffer = ""
                    elif event.key == pygame.K_BACKSPACE:
                        text_buffer = text_buffer[:-1]
                    elif event.unicode and event.unicode.isprintable():
                        text_buffer += event.unicode
                    continue

                if (event.key == pygame.K_w and ctrl_held) or \
                   (event.key == pygame.K_F4 and alt_held) or \
                    event.key == pygame.K_ESCAPE:
                    return

                if event.key == pygame.K_s and ctrl_held:
                    fname = save_canvas(canvas)
                    pygame.display.set_caption(f"Saved: {fname}")

                key_tool_map = {
                    pygame.K_1: 'draw',      pygame.K_2: 'line',
                    pygame.K_3: 'rectangle', pygame.K_4: 'circle',
                    pygame.K_5: 'eraser',    pygame.K_6: 'fill',
                    pygame.K_7: 'text',      pygame.K_8: 'square',
                    pygame.K_9: 'right_tri', pygame.K_0: 'eq_tri',
                    pygame.K_MINUS: 'rhombus',
                }
                if event.key in key_tool_map:
                    tool = key_tool_map[event.key]

                if event.key == pygame.K_F1:   brush_idx = 0
                elif event.key == pygame.K_F2: brush_idx = 1
                elif event.key == pygame.K_F3: brush_idx = 2

                if event.key == pygame.K_c and not ctrl_held:
                    canvas.fill((0, 0, 0))
                    points = []

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                for i, rect in enumerate(tool_rects):
                    if rect.collidepoint(event.pos):
                        tool = TOOLS[i]
                        text_active = False
                        break

                for i, rect in enumerate(size_rects):
                    if rect.collidepoint(event.pos):
                        brush_idx = i
                        break

                for i, rect in enumerate(palette_rects):
                    if rect.collidepoint(event.pos):
                        custom_color = PALETTE_COLORS[i]
                        break

                if not on_canvas(event.pos):
                    continue

                cp = to_canvas(event.pos)

                if tool == 'text':
                    text_active = True
                    text_pos    = event.pos
                    text_buffer = ""
                    continue

                if tool == 'fill':
                    flood_fill(canvas, cp[0], cp[1], get_color())
                    continue

                if tool in SHAPE_TOOLS:
                    shape_start = event.pos

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if shape_start and tool in SHAPE_TOOLS:
                    if on_canvas(mouse_pos):
                        draw_shape(canvas, tool,
                                   to_canvas(shape_start),
                                   to_canvas(mouse_pos),
                                   get_color(), brush)
                    shape_start = None

                if tool == 'draw':
                    points = []

            if event.type == pygame.MOUSEMOTION and on_canvas(mouse_pos):
                cp = to_canvas(mouse_pos)
                if tool == 'draw' and mouse_buttons[0]:
                    points.append(mouse_pos)
                    if len(points) >= 2:
                        draw_pencil_segment(canvas,
                                            to_canvas(points[-2]),
                                            to_canvas(points[-1]),
                                            brush, get_color())
                elif tool == 'eraser' and mouse_buttons[0]:
                    pygame.draw.circle(canvas, (0, 0, 0), cp, brush * 2)

        # ── Render ───────────────────────────────────────────────────────────
        screen.fill((20, 20, 20))
        screen.blit(canvas, (0, CANVAS_TOP))

        if shape_start and mouse_buttons[0] and tool in SHAPE_TOOLS and on_canvas(mouse_pos):
            draw_shape(screen, tool,
                       to_canvas(shape_start),
                       to_canvas(mouse_pos),
                       get_color(), brush)

        if tool == 'eraser':
            pygame.draw.circle(screen, (200, 200, 200), mouse_pos, brush * 2, 2)

        if text_active:
            preview = font_text.render(text_buffer + "|", True, get_color())
            screen.blit(preview, text_pos)

        # Top toolbar
        pygame.draw.rect(screen, (30, 30, 30), (0, 0, W, CANVAS_TOP))
        pygame.draw.line(screen, (80, 80, 80), (0, CANVAS_TOP), (W, CANVAS_TOP), 1)

        for t, rect, label in zip(TOOLS, tool_rects, TOOL_LABELS):
            color_btn = (70, 100, 210) if t == tool else (55, 55, 55)
            pygame.draw.rect(screen, color_btn, rect, border_radius=4)
            pygame.draw.rect(screen, (120, 120, 120), rect, 1, border_radius=4)
            screen.blit(font.render(label, True, (255, 255, 255)),
                        (rect.x + 3, rect.y + 6))

        for i, (rect, label) in enumerate(zip(size_rects, BRUSH_LABELS)):
            color_btn = (50, 160, 80) if i == brush_idx else (55, 55, 55)
            pygame.draw.rect(screen, color_btn, rect, border_radius=4)
            pygame.draw.rect(screen, (120, 120, 120), rect, 1, border_radius=4)
            screen.blit(font.render(label, True, (255, 255, 255)),
                        (rect.x + 5, rect.y + 6))

        # Bottom palette bar
        pygame.draw.rect(screen, (30, 30, 30), (0, H - BOTTOM_BAR, W, BOTTOM_BAR))
        pygame.draw.line(screen, (80, 80, 80), (0, H - BOTTOM_BAR), (W, H - BOTTOM_BAR), 1)

        for col, rect in zip(PALETTE_COLORS, palette_rects):
            pygame.draw.rect(screen, col, rect, border_radius=4)
            if custom_color == col:
                pygame.draw.rect(screen, (255, 255, 255), rect, 2, border_radius=4)

        pygame.draw.rect(screen, get_color(),
                         pygame.Rect(300, PAL_Y, SWATCH, SWATCH), border_radius=4)

        hint = font.render(
            f"Brush: {brush}px  |  F1/F2/F3=S/M/L  |  C=Clear  |  "
            "Ctrl+S=Save PNG  |  Text: click→type→Enter / Esc=cancel",
            True, (160, 160, 160))
        screen.blit(hint, (340, PAL_Y + 8))

        pygame.display.flip()
        clock.tick(60)


main()