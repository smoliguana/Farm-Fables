import pygame
from settings import *
from support import *
from pytmx.util_pygame import load_pygame
from random import choice

class SoilTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = layers['soil']

class WaterTile(pygame.sprite.Sprite):
    def __init__(self, pos,surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = layers['soil water']

class Plant(pygame.sprite.Sprite):
    def __init__(self, plant_type, groups, soil, check_watered):
        super().__init__(groups)
        #setup
        self.plant_type = plant_type
        self.frames = import_folder(f'../graphics/fruit/{plant_type}')
        self.soil = soil
        self.check_watered = check_watered
        #plant growth
        self.age = 0
        self.max_age = len(self.frames) - 1
        self.grow_speed = Grow_speed[plant_type]
        self.harvestable = False
        #sprite
        self.image = self.frames[self.age]
        if plant_type == 'corn': self.y_offset = -16 
        else: self.y_offset = -8
        self.rect = self.image.get_rect(midbottom = soil.rect.midbottom + pygame.math.Vector2(0,self.y_offset))
        self.z = layers['ground plant']

    def grow(self):
        if self.check_watered(self.rect.center):
            self.age += self.grow_speed
            if int(self.age) > 0:
                self.z = layers['main']
                self.hitbox = self.rect.copy().inflate(-26,-self.rect.height *0.4)
            #making sure the plant age don't go over the max age
            if self.age >= self.max_age:
                self.age = self.max_age
                self.harvestable = True
            self.image = self.frames[int(self.age)]
            self.rect = self.image.get_rect(midbottom = self.soil.rect.midbottom + pygame.math.Vector2(0,self.y_offset))

        
class SoilLayer:
    def __init__(self, all_sprites, collision_sprites):
        #sprite groups
        self.all_sprites = all_sprites
        self.collision_sprites = collision_sprites
        self.soil_sprites = pygame.sprite.Group()
        self.water_sprites = pygame.sprite.Group()
        self.plant_sprites = pygame.sprite.Group()
        #graphics
        self.soil_surfs = import_folder_dict('../graphics/soil/')
        self.water_surfs = import_folder('../graphics/soil_water/')

        self.create_soil_grid()
        self.create_hit_rects()
        #sfx
        self.hoe_sound = pygame.mixer.Sound('../audio/hoe.wav')
        self.hoe_sound.set_volume(0.1)
        self.plant_sound = pygame.mixer.Sound('../audio/plant.wav')
        self.plant_sound.set_volume(0.2)

    def create_soil_grid(self):
        ground = pygame.image.load('../graphics/world/ground.png')
        h_tiles, v_tiles = ground.get_width()// tile_size, ground.get_height()// tile_size
        self.grid = [[[] for col in range(h_tiles)] for row in range(v_tiles)]
        for x, y, surf in load_pygame('../data/map.tmx').get_layer_by_name('Farmable').tiles():
            self.grid[y][x].append('F')

    def create_hit_rects(self):
        self.hit_rects = []
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'F' in cell:
                    x = index_col * tile_size
                    y = index_row * tile_size
                    rect = pygame.Rect(x,y, tile_size,tile_size)
                    self.hit_rects.append(rect)

    def get_hit(self, point):
        for rect in self.hit_rects:
            if rect.collidepoint(point):
                self.hoe_sound.play()
                x = rect.x // tile_size
                y = rect.y // tile_size
                if 'F' in self.grid[y][x]:
                    self.grid[y][x].append('X')
                    self.create_soil_tiles()
                    if self.raining:
                        self.water_all()

    def water(self,target_pos):
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(target_pos):
                x = soil_sprite.rect.x //tile_size
                y = soil_sprite.rect.y //tile_size
                self.grid[y][x].append('W')

                #water sprite
                WaterTile(pos = soil_sprite.rect.topleft, 
                          surf = choice(self.water_surfs), 
                          groups = [self.all_sprites,self.water_sprites])

    def water_all(self):
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'X' in cell and 'W' not in cell:
                    cell.append('W')
                    x = index_col * tile_size
                    y = index_row * tile_size
                    WaterTile(pos = (x,y),
                              surf =choice(self.water_surfs),
                              groups = [self.all_sprites, self.water_sprites])
                    
    def remove_water(self):
        #destroy water sprites
        for sprite in self.water_sprites.sprites():
            sprite.kill()
        #clean grid
        for row in self.grid:
            for cell in row:
                if 'W' in cell:
                    cell.remove('W')
    
    def check_watered(self, pos):
        x = pos[0] // tile_size
        y = pos[1] // tile_size
        cell = self.grid[y][x]
        is_watered = 'W' in cell
        return is_watered
    
    def plant_seed(self, target_pos, seed):
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(target_pos):
                self.plant_sound.play()
                x = soil_sprite.rect.x // tile_size
                y = soil_sprite.rect.y // tile_size
                if 'P' not in self.grid[y][x]:
                    self.grid[y][x].append('P')
                    Plant(seed, [self.all_sprites, self.plant_sprites, self.collision_sprites], soil_sprite, self.check_watered)

    def update_plants(self):
        for plant in self.plant_sprites.sprites():
            plant.grow()

    def create_soil_tiles(self):
        self.soil_sprites.empty()
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'X' in cell:
                    #check the tiles surrounding the soil tile
                    t = 'X' in self.grid[index_row - 1][index_col]
                    b = 'X' in self.grid[index_row + 1][index_col]
                    r = 'X' in row[index_col + 1]
                    l = 'X' in row[index_col - 1]
                    tile_type = 'o'

                    #change soil img if all sides are soil
                    if all((t,b,r,l)): tile_type = 'x'
                    #change img if any of the horizontal sides are soil
                    if l and not any((t,r,b)): tile_type = 'r'
                    if r and not any((t,l,b)): tile_type = 'l'
                    if l and r and not any((t,b)): tile_type = 'lr'
                    #change img if any of the vertical sides are soil
                    if t and not any((l,r,b)): tile_type = 'b'
                    if b and not any((t,l,r)): tile_type = 't'
                    if t and b and not any((r,l)): tile_type = 'tb'
                    #change img for the corners of the soil
                    if b and r and not any((t,l)): tile_type = 'tl'
                    if b and l and not any((t,r)): tile_type = 'tr'
                    if t and r and not any((b,l)): tile_type = 'bl'
                    if t and l and not any((b,r)): tile_type = 'br'
                    # T shapes
                    if all((t,b,r)) and not l: tile_type = 'tbr'
                    if all((t,b,l)) and not r: tile_type = 'tbl'
                    if all((l,r,t)) and not b: tile_type = 'lrt'
                    if all((l,r,b)) and not t: tile_type = 'lrb'
                    #middle parts :-)(EAAUUURGHHHHHH)
                    if all((b,l,r)) and not t: tile_type = 'tm'
                    if all((t,l,r)) and not b: tile_type = 'bm'
                    if all((t,b,r)) and not l: tile_type = 'lm'
                    if all((t,b,l)) and not r: tile_type = 'rm'

                    SoilTile(pos = (index_col * tile_size, index_row * tile_size), 
                             surf = self.soil_surfs[tile_type], 
                             groups = [self.all_sprites,self.soil_sprites])