import pygame
import random
from generator import TerrainGenerator
from renderer import Renderer
from player import Camera

pygame.init()
WIDTH, HEIGHT = 800, 600
FPS = 100



def handle_events(terrain_generator, camera, renderer):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False
            elif event.key == pygame.K_r: # regen TODO
                terrain_seed  = random.randint(1000, 9999)
                variant_seed  = random.randint(1000, 9999)
                moisture_seed = random.randint(1000, 9999)
                biome_seed    = random.randint(1000, 9999)
                
                terrain_generator.regenerate_terrain(
                    terrain_seed, variant_seed, moisture_seed, biome_seed
                )
                
                print("-"*80 + f"\nSeeds: terrain={terrain_seed}, variant={variant_seed}, "
                      f"moisture={moisture_seed}, biome={biome_seed}")
    
    keys = pygame.key.get_pressed()
    camera.update(keys)
    
    renderer.handle_zoom(keys)
    
    return True

size=600
terrain_seed  = random.randint(1000, 9999)
variant_seed  = random.randint(1000, 9999)
moisture_seed = random.randint(1000, 9999)
biome_seed    = random.randint(1000, 9999)
    
print(f"Seeds: terrain={terrain_seed}, variant={variant_seed}, "
    f"moisture={moisture_seed}, biome={biome_seed}")

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Funny game")

terrain_generator = TerrainGenerator(
    size=size, 
    terrain_seed=terrain_seed,
    terrain_variant_seed=variant_seed,
    moisture_seed=moisture_seed,
    biome_seed=biome_seed
)

camera = Camera(
    initial_x=size // 2,
    initial_y=size // 2,
    speed=0.3
)

renderer = Renderer(
    screen=screen, 
    terrain_generator=terrain_generator,
    camera=camera,
    width=WIDTH,
    height=HEIGHT
)

clock = pygame.time.Clock()
while True:
    running = handle_events(terrain_generator, camera, renderer)

    renderer.draw_terrain()
    renderer.display_debug_info(clock.get_fps())
    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()
