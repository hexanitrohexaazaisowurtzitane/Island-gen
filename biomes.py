COLORS = {
    'OCEAN': (0, 62, 178),
    'SEA': (9, 82, 198),
    'DRY_SAND': (194, 178, 129),
    'SAND': (164, 148, 99),
    'WET_SAND': (134, 118, 69),
    'DRY_GRASS': (40, 77, 0),
    'GRASS': (60, 97, 20),
    'WET_GRASS': (90, 127, 50),
    'MOUNTAIN_SNOW': (235, 235, 235),
    'MOUNTAIN_ORE': (140, 142, 123),
    'MOUNTAIN': (160, 162, 143),

    'DESERT': (242, 209, 107),
    'DESERT_DUNES': (230, 190, 85),
    'FOREST': (21, 71, 52),
    'DENSE_FOREST': (18, 56, 40),
    'SAVANNA': (177, 166, 87),
    'SAVANNA_SCRUB': (150, 142, 75),
    'JUNGLE': (20, 83, 45),
    'JUNGLE_DENSE': (15, 60, 35),
    # variants
    'GRASSLAND': (76, 115, 36),
    'GRASSLAND_LUSH': (96, 140, 43),
    'GRASSLAND_DRY': (147, 155, 83)
}

TERRAIN_TYPES = {
    'OCEAN': 'OCEAN',
    'SEA': 'SEA',
    'DRY_SAND': 'DRY_SAND',
    'SAND': 'SAND',
    'WET_SAND': 'WET_SAND',
    'DRY_GRASS': 'DRY_GRASS',
    'GRASS': 'GRASS',
    'WET_GRASS': 'WET_GRASS',
    'MOUNTAIN_SNOW': 'MOUNTAIN_SNOW',
    'MOUNTAIN_ORE': 'MOUNTAIN_ORE',
    'MOUNTAIN': 'MOUNTAIN',

    'DESERT': 'DESERT',
    'DESERT_DUNES': 'DESERT_DUNES',
    'FOREST': 'FOREST',
    'DENSE_FOREST': 'DENSE_FOREST',
    'SAVANNA': 'SAVANNA',
    'SAVANNA_SCRUB': 'SAVANNA_SCRUB',
    'JUNGLE': 'JUNGLE',
    'JUNGLE_DENSE': 'JUNGLE_DENSE',

    # added grassland as a type and fallback for transition between biomes
    'GRASSLAND': 'GRASSLAND',
    'GRASSLAND_LUSH': 'GRASSLAND_LUSH',
    'GRASSLAND_DRY': 'GRASSLAND_DRY'
}

def determine_terrain_type(
    terrain_noise, variant_noise, moisture_noise, desert_influence, 
    savanna_influence, forest_influence, jungle_influence, grassland_influence
    ):
    """Set type w noise values"""
    
    # sea n ocean
    if terrain_noise < 0.2:   return TERRAIN_TYPES['OCEAN'], COLORS['OCEAN']
    elif terrain_noise < 0.4: return TERRAIN_TYPES['SEA'],   COLORS['SEA']
    elif terrain_noise < 0.45:
        # sand
        if variant_noise < -0.2:  return TERRAIN_TYPES['WET_SAND'], COLORS['WET_SAND']
        elif variant_noise < 0.2: return TERRAIN_TYPES['SAND'],     COLORS['SAND']
        else:                     return TERRAIN_TYPES['DRY_SAND'], COLORS['DRY_SAND']
    elif terrain_noise < 0.6:
        # mid elev biomes
        # params=temperature, moisture, biome_influence
        desert_score =  desert_influence  * 1.5 + (variant_noise * 0.5) - (moisture_noise * 0.8)
        savanna_score = savanna_influence * 1.5 + (variant_noise * 0.3) - (moisture_noise * 0.4)
        forest_score =  forest_influence  * 1.5 - (variant_noise * 0.3) + (moisture_noise * 0.5)
        jungle_score =  jungle_influence  * 1.5 + (variant_noise * 0.3) + (moisture_noise * 0.8)
        # grassland score
        grassland_score = grassland_influence * 1.5 - abs(variant_noise * 0.2) + (moisture_noise * 0.3)
        grassland_score *= 1.2
        
        # get dominant
        biome_scores = {
            'DESERT': desert_score,
            'SAVANNA': savanna_score,
            'FOREST': forest_score,
            'JUNGLE': jungle_score,
            'GRASSLAND': grassland_score
        }
        dominant_biome = max(biome_scores, key=biome_scores.get)
        
        if dominant_biome == 'DESERT':
            if variant_noise > 0.3 or desert_score > 1.5:
                  return TERRAIN_TYPES['DESERT_DUNES'], COLORS['DESERT_DUNES']
            else: return TERRAIN_TYPES['DESERT'],       COLORS['DESERT']
                
        elif dominant_biome == 'SAVANNA':
            if moisture_noise < -0.3: return TERRAIN_TYPES['SAVANNA_SCRUB'], COLORS['SAVANNA_SCRUB']
            else:                     return TERRAIN_TYPES['SAVANNA'],       COLORS['SAVANNA']
                
        elif dominant_biome == 'FOREST':
            if moisture_noise > 0.3:  return TERRAIN_TYPES['DENSE_FOREST'], COLORS['DENSE_FOREST']
            else:                     return TERRAIN_TYPES['FOREST'],       COLORS['FOREST']
                
        elif dominant_biome == 'JUNGLE':
            if moisture_noise > 0.4:  return TERRAIN_TYPES['JUNGLE_DENSE'], COLORS['JUNGLE_DENSE']
            else:                     return TERRAIN_TYPES['JUNGLE'],       COLORS['JUNGLE']
                
        elif dominant_biome == 'GRASSLAND':
            if moisture_noise > 0.2:  
                  return TERRAIN_TYPES['GRASSLAND_LUSH'], COLORS['GRASSLAND_LUSH']
            elif moisture_noise < -0.2 or variant_noise > 0.3:
                  return TERRAIN_TYPES['GRASSLAND_DRY'], COLORS['GRASSLAND_DRY']
            else: return TERRAIN_TYPES['GRASSLAND'],     COLORS['GRASSLAND']
        
        # fallback to grassland
        else:
            if variant_noise < -0.2:  return TERRAIN_TYPES['DRY_GRASS'],    COLORS['DRY_GRASS']
            elif variant_noise < 0.2: return TERRAIN_TYPES['GRASS'],        COLORS['GRASS']
            else:                     return TERRAIN_TYPES['WET_GRASS'],    COLORS['WET_GRASS']
    else: # high elev mountain
        if variant_noise < -0.2:      return TERRAIN_TYPES['MOUNTAIN_SNOW'], COLORS['MOUNTAIN_SNOW']
        elif variant_noise < 0.2:     return TERRAIN_TYPES['MOUNTAIN_ORE'],  COLORS['MOUNTAIN_ORE']
        else:                         return TERRAIN_TYPES['MOUNTAIN'],      COLORS['MOUNTAIN']