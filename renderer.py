import pygame

CELL_SIZE = 16  # cell
SCALE = 0.05    # scale

# chunk render and culling will not work with the main.py script
# as i haven't implemented it there. Might take a few seconds to generate because of that
# This was part of a game that i gave up on
# some of the code may not be used

class Renderer:
    def __init__(self, screen, terrain_generator, camera, width, height):
        self.screen = screen
        self.terrain_generator = terrain_generator
        self.camera = camera
        self.width = width
        self.height = height
        
        self.camera.set_terrain_size(terrain_generator.size)
        
        self.chunk_size = 32 
        self.chunks = {}
    
    def handle_zoom(self, keys):
        global SCALE
        _scale = SCALE

        if keys[pygame.K_q]: SCALE = max(0.05, SCALE - 0.01)
        if keys[pygame.K_e]: SCALE = min(2.0, SCALE + 0.01)
            
        # clear cache to render correctly
        if abs(_scale - SCALE) > 0.1:
            self.chunks = {}
            print(f"SCALE={SCALE:.2f}; Cache data resets")
    
    def render_chunk(self, chunk_x, chunk_y):
        chunk_key = (chunk_x, chunk_y)  # assigned as chunk key
        
        if chunk_key in self.chunks:
            return self.chunks[chunk_key]
        
        chunk_surface = pygame.Surface((self.chunk_size * CELL_SIZE, self.chunk_size * CELL_SIZE))

        for x_offset in range(self.chunk_size):
            for y_offset in range(self.chunk_size):
                
                x = chunk_x * self.chunk_size + x_offset
                y = chunk_y * self.chunk_size + y_offset
                
                # outof bounds
                if x >= self.terrain_generator.size or y >= self.terrain_generator.size or x < 0 or y < 0:
                    continue
                
                info = self.terrain_generator.get_terrain_info(x, y)


                pygame.draw.rect(chunk_surface, info['color'], 
                (x_offset * CELL_SIZE, y_offset * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        

        self.chunks[chunk_key] = chunk_surface
        return chunk_surface

    def draw_terrain(self):
        """draw visible chunks"""


        self.screen.fill((0, 0, 0))
        
        # get visible chunks
        start_chunk_x = int((self.camera.x - self.width // (2 * CELL_SIZE * SCALE)) / self.chunk_size)
        start_chunk_y = int((self.camera.y - self.height // (2 * CELL_SIZE * SCALE)) / self.chunk_size)

        chunks_x = int(self.width / (self.chunk_size * CELL_SIZE * SCALE)) + 2
        chunks_y = int(self.height / (self.chunk_size * CELL_SIZE * SCALE)) + 2
        
        chunks_rendered = 0
        


        for chunk_offset_x in range(chunks_x):
            for chunk_offset_y in range(chunks_y):
                chunk_x = start_chunk_x + chunk_offset_x
                chunk_y = start_chunk_y + chunk_offset_y
                

                if (chunk_x < 0 or chunk_y < 0 or 
                    chunk_x * self.chunk_size >= self.terrain_generator.size or 
                    chunk_y * self.chunk_size >= self.terrain_generator.size):
                    continue #out
                
        
                chunk_surface = self.render_chunk(chunk_x, chunk_y)
                chunks_rendered += 1
                
                # get screen pos
                import math
                screen_x = math.floor(
                    (   # pixel align
                        chunk_x * self.chunk_size - self.camera.x + 
                        self.width // (2 * CELL_SIZE * SCALE)
                    ) * CELL_SIZE * SCALE)
                screen_y = math.floor(
                    (
                        chunk_y * self.chunk_size - self.camera.y + 
                        self.height // (2 * CELL_SIZE * SCALE)
                    ) * CELL_SIZE * SCALE)
                
                # scale n draw
                if SCALE != 1.0:
                    scaled_size = (
                        int(self.chunk_size * CELL_SIZE * SCALE) + 1, # no gaps
                        int(self.chunk_size * CELL_SIZE * SCALE) + 1
                        )
                    scaled_chunk = pygame.transform.scale(chunk_surface, scaled_size)
                    self.screen.blit(scaled_chunk, (screen_x, screen_y))

                else: self.screen.blit(chunk_surface, (screen_x, screen_y))

    def display_debug_info(self, fps):

        mouse_x, mouse_y = pygame.mouse.get_pos()
        world_x, world_y = self.camera.screen_to_world(mouse_x, mouse_y, self.width, self.height)
        
        if (0 <= world_x < self.terrain_generator.size and 
            0 <= world_y < self.terrain_generator.size):
            
            info = self.terrain_generator.get_terrain_info(world_x, world_y)
            
            
            font = pygame.font.SysFont(None, 16)
            
            line_height = 16
            start_y = 5
            
            text1 = font.render(f"Type: {info['type']} | Pos: ({world_x}, {world_y})", True, (255, 255, 255))
            self.screen.blit(text1, (10, start_y))
            
            text2 = font.render(
                f"Height: {info['terrain_noise']:.2f} | Temp: {info['variant_noise']:.2f} | " +
                f"Moisture: {info['moisture_noise']:.2f}", 
                True, (255, 255, 255)
            )
            self.screen.blit(text2, (10, start_y + line_height))
            
            text3 = font.render(
                f"Biome - D: {info['desert_influence']:.2f} | S: {info['savanna_influence']:.2f} | " +
                f"F: {info['forest_influence']:.2f}", 
                True, (255, 255, 255)
            )
            self.screen.blit(text3, (10, start_y + line_height * 2))
            
            text4 = font.render(
                f"Biome - J: {info['jungle_influence']:.2f} | G: {info['grassland_influence']:.2f}", 
                True, (255, 255, 255)
            )
            self.screen.blit(text4, (10, start_y + line_height * 3))
            
            text5 = font.render(
                f"FPS: {int(fps)} | Chunks: {len(self.chunks)} | " +
                f"Cache: {len(self.terrain_generator.terrain_cache)}", 
            True, (255, 255, 255)
            )
            self.screen.blit(text5, (10, start_y + line_height * 4))
            
            text6 = font.render("WASD: Move | Q/E: Zoom | R: Regen | ESC: Exit", 
                            True, (255, 255, 255))
            self.screen.blit(text6, (10, self.height - 20))