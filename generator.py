from opensimplex import OpenSimplex
from functools import lru_cache

class TerrainGenerator:
    def __init__(self, size=600, terrain_seed=None, terrain_variant_seed=None, 
                 moisture_seed=None, biome_seed=None):

        self.size = size
        
        self.terrain_seed = terrain_seed
        self.variant_seed = terrain_variant_seed
        self.moisture_seed = moisture_seed
        self.biome_seed = biome_seed
        
        self._initialize_noise_generators()
        
        self.octaves = 20 #15
        self.frequency = 0.00625
        self.persistence = 0.6
        self.blur = 100
        
        self.biome_octaves = 3
        self.biome_frequency = 0.003 # big features
        self.biome_persistence = 0.5
        
        self.terrain_cache = {}
        
        print(f"Octaves: terrain={self.octaves}, biome={self.biome_octaves}")
    
    def _initialize_noise_generators(self):
        self.terrain_noise  = OpenSimplex(seed=self.terrain_seed)
        self.variant_noise  = OpenSimplex(seed=self.variant_seed)
        self.moisture_noise = OpenSimplex(seed=self.moisture_seed)
        self.biome_noise    = OpenSimplex(seed=self.biome_seed)
    
    def regenerate_terrain(self, terrain_seed, variant_seed, moisture_seed, biome_seed):
        # random new seeds n regen
        self.terrain_seed = terrain_seed
        self.variant_seed = variant_seed
        self.moisture_seed = moisture_seed
        self.biome_seed = biome_seed
        
        self._initialize_noise_generators()
        
        self.terrain_cache = {}
        self.cached_fractal_noise.cache_clear()
    
    @lru_cache(maxsize=8192)
    def cached_fractal_noise(self, x, y, noise_type, octaves, frequency, persistence):
        """cached fractal noise thingy"""
        if   noise_type == 'terrain':  noise_func = self.terrain_noise
        elif noise_type == 'variant':  noise_func = self.variant_noise
        elif noise_type == 'moisture': noise_func = self.moisture_noise
        elif noise_type == 'biome':    noise_func = self.biome_noise
        
        else: raise ValueError(f"unknown noise: {noise_type}")
            
        # less for biome noise
        if noise_type == 'biome' and octaves > 2: octaves = 2
            
        value = 0.0
        amplitude = 1.0
        max_value = 0.0
        
        for i in range(octaves):
            freq = frequency * (2 ** i)
            value += noise_func.noise2(x * freq, y * freq) * amplitude
            max_value += amplitude
            amplitude *= persistence
            
        return value / max_value

    def fractal_noise(self, x, y, noise_func, octaves, frequency, persistence):
        """generate fractal at pos"""
        # map noise to cachable* type
        if   noise_func == self.terrain_noise:  noise_type = 'terrain'
        elif noise_func == self.variant_noise:  noise_type = 'variant'
        elif noise_func == self.moisture_noise: noise_type = 'moisture'
        elif noise_func == self.biome_noise:    noise_type = 'biome'
        else:
            # fall back to non cached
            value = 0.0
            amplitude = 1.0
            max_value = 0.0
            
            for i in range(octaves):
                freq   = frequency * (2 ** i)
                value += noise_func.noise2(x * freq, y * freq) * amplitude
                max_value += amplitude
                amplitude *= persistence
                
            return value / max_value
            
        return self.cached_fractal_noise(x, y, noise_type, octaves, frequency, persistence)

    def box_gradient(self, x, y):
        """box gradient for edges"""
        min_coord_blur = self.blur
        max_coord_blur = self.size - self.blur
        
        # get smallest distant from edges
        distances = [
            x,
            y,
            self.size - x,
            self.size - y
        ]
        
        min_dist = min(distances)
        
        if min_dist >= min_coord_blur and min_dist <= max_coord_blur:
            return 1
        
        if min_dist < min_coord_blur:
            return min_dist / min_coord_blur
        
        if min_dist > max_coord_blur:
            return max(0, (self.size - min_dist) / (self.size - max_coord_blur))
            
        return 1

    def get_biome_influence(self, x, y):
        """do biome influence for regions"""
        # low freq here
        desert_influence = self.fractal_noise(
            x, y + 1000, self.biome_noise, 
            self.biome_octaves, self.biome_frequency, 
            self.biome_persistence
            )
        
        savanna_influence = self.fractal_noise(
            x + 1000, y, self.biome_noise, 
            self.biome_octaves, self.biome_frequency, 
            self.biome_persistence
            )
        
        forest_influence = self.fractal_noise(
            x, y + 2000, self.biome_noise, 
            self.biome_octaves, self.biome_frequency, 
            self.biome_persistence
            )
        
        jungle_influence = self.fractal_noise(
            x + 2000, y, self.biome_noise, 
            self.biome_octaves, self.biome_frequency, 
            self.biome_persistence
            )
        
        grassland_influence = self.fractal_noise(
            x + 3000, y + 3000, self.biome_noise, 
            self.biome_octaves, self.biome_frequency, 
            self.biome_persistence
            )
        
        # norm to 0, 1
        desert_influence     = (desert_influence  + 1) / 2
        savanna_influence    = (savanna_influence + 1) / 2
        forest_influence     = (forest_influence  + 1) / 2
        jungle_influence     = (jungle_influence  + 1) / 2
        grassland_influence  = (grassland_influence + 1) / 2
        
        return desert_influence, savanna_influence, forest_influence, jungle_influence, grassland_influence

    def get_terrain_info(self, x, y):
        """terrain data"""
        if (x, y) in self.terrain_cache:
            return self.terrain_cache[(x, y)]
            
        # do noise w border
        terrain_noise = (
            self.fractal_noise(
                x, y, self.terrain_noise, self.octaves, 
                self.frequency, self.persistence) + 1
                ) / 2
        terrain_noise = terrain_noise + (self.box_gradient(x, y) - 1)
        
        # do variant noise for temp
        variant_noise = self.fractal_noise(
            x, y, self.variant_noise, 
            self.octaves, self.frequency, 
            self.persistence
            )
        
        # do moisture 
        moisture_noise = self.fractal_noise(
            x, y, self.moisture_noise, 
            self.octaves, self.frequency, 
            self.persistence
            )



        influences = self.get_biome_influence(x, y)
        desert_influence, savanna_influence, forest_influence, jungle_influence, grassland_influence = influences
        
        info = {
            'x': x,
            'y': y,
            'type': None,
            'color': None,
            'variant_noise': variant_noise,
            'moisture_noise': moisture_noise,
            'terrain_noise': terrain_noise,
            'desert_influence': desert_influence,
            'savanna_influence': savanna_influence,
            'forest_influence': forest_influence,
            'jungle_influence': jungle_influence,
            'grassland_influence': grassland_influence
        }
        
        # set biome n terrain type
        from biomes import determine_terrain_type

        terrain_type, color = determine_terrain_type(
            terrain_noise, variant_noise, moisture_noise, 
            desert_influence, savanna_influence, forest_influence,
            jungle_influence, grassland_influence
        )
        
        info['type'] = terrain_type
        info['color'] = color

        self.terrain_cache[(x, y)] = info
        return info