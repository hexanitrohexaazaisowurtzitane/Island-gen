import pygame

class Camera:
    def __init__(self, initial_x, initial_y, speed=0.3):
        self.x = initial_x
        self.y = initial_y
        self.speed = speed
        self.terrain_size = 600
        
    def update(self, keys):
        from renderer import SCALE
        if keys[pygame.K_w]:  self.y -= self.speed / SCALE
        if keys[pygame.K_s]:  self.y += self.speed / SCALE
        if keys[pygame.K_a]:  self.x -= self.speed / SCALE
        if keys[pygame.K_d]:  self.x += self.speed / SCALE
            
        # keep in sceen
        self.x = max(0, min(self.terrain_size, self.x))
        self.y = max(0, min(self.terrain_size, self.y))
        
    def set_terrain_size(self, size):  self.terrain_size = size
        
    def screen_to_world(self, screen_x, screen_y, width, height):
        """convert coordinates"""
        from renderer import SCALE, CELL_SIZE
        
        world_x = int(self.x + (screen_x -  width // 2) / (CELL_SIZE * SCALE))
        world_y = int(self.y + (screen_y - height // 2) / (CELL_SIZE * SCALE))
        
        return world_x, world_y