import pygame

class Ball:
    def __init__(self, screen_width, screen_height):
        self.radius = 25
        self.color = (255, 0, 0)  # Red
        self.x = screen_width // 2
        self.y = screen_height // 2
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.speed = 20

    def move(self, direction):
        new_x, new_y = self.x, self.y
        
        if direction == "UP":
            new_y -= self.speed
        elif direction == "DOWN":
            new_y += self.speed
        elif direction == "LEFT":
            new_x -= self.speed
        elif direction == "RIGHT":
            new_x += self.speed

        if (self.radius <= new_x <= self.screen_width - self.radius and 
            self.radius <= new_y <= self.screen_height - self.radius):
            self.x, self.y = new_x, new_y

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)