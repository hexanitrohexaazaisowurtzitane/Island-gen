###### Based on https://codesandbox.io/p/sandbox/procedural-map-generator-tsu2c
# Cool Island Generator

![Seeds:terrain=6417, variant=6976, moisture=7617, biome=3914](https://github.com/user-attachments/assets/28ecfdaf-1a6b-437e-b75d-74df91303bb5)


2d generation project that was a map generator for a game i gave up working on.

Uses opensimplex (0.4.5.1) for noise gen, contains `[forest, desert, jungle, savanna, grassland, mountains, sea, ocean, puddles]` 

Also contains a chunk system that can be used (not implemented in main script though)

#### Biome Logic 
Biomes are generated using 4 params:
```
* terrain : ocean -> beach -> mid-lvl -> mountains
* moisture : wet -> dry noise
* influence : main biome influence for regions
* variant : hot -> cold noise (temperature)
```

Process:
* Set base terrain by elevation
* Set mid-level biome types scoring using influence, variation and moisture params
* Set highest score biome as dominant
* Add variation with smaller biome varients
* Blend biomes


#### Adding new content
Can be made almost entirely in biomes.py, but also needs influence adjustments to the generator.

Biomes consist on a color and terrain type for now, but I might change this later into something more specific.
