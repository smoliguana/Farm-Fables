import pygame
import pytmx
from pytmx.util_pygame import load_pygame
from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic, Water, WildFlower, Tree, Interaction, Particle
from support import *
from transition import Transition
from soil import SoilLayer
from sky import Rain, Sky
from random import randint
from menu import Menu
from inventory import Inventory




class Level:
    def __init__(self):
      #get display surface
      self.display_surface = pygame.display.get_surface() 
      #sprite groups
      self.all_sprites = CameraGroup()
      self.collision_sprites = pygame.sprite.Group()
      self.tree_sprites = pygame.sprite.Group()
      self.interaction_sprite = pygame.sprite.Group()

      self.soil_layer = SoilLayer(self.all_sprites, self.collision_sprites)
      self.setup()
      self.overlay = Overlay(self.player)
      self.transition = Transition(self.reset,self.player)

      #sky
      self.rain = Rain(self.all_sprites)
      self.raining = randint(0,10) > 7
      self.soil_layer.raining = self.raining
      self.sky = Sky()

      #shop
      self.menu = Menu(self.player, self.toggle_shop)
      self.shop_active = False
      #inventory
      self.inventory = Inventory(self.player, self.open_inventory)
      self.inventory_active = False
      #sfx
      self.success = pygame.mixer.Sound('../audio/success.wav')
      self.success.set_volume(0.3)
      self.bg_music = pygame.mixer.Sound('../audio/music.mp3')
      self.bg_music.play(loops = -1)

    def setup(self):
       tmx_data = load_pygame('../data/map.tmx')
       #house
       for layer in ['HouseFloor', 'HouseFurnitureBottom']:
         for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
            Generic((x * tile_size, y * tile_size),surf,self.all_sprites,layers['house bottom'])

       for layer in ['HouseWalls', 'HouseFurnitureTop']:
         for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
            Generic((x * tile_size, y * tile_size),surf,self.all_sprites,layers['main'])
      #fence
         for x, y, surf in tmx_data.get_layer_by_name('Fence').tiles():
            Generic((x * tile_size, y * tile_size),surf,[self.all_sprites, self.collision_sprites],layers['main'])
      #water
         water_frames = import_folder('../graphics/water')
         for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
            Water((x * tile_size, y * tile_size),water_frames, self.all_sprites)
      #trees
         for obj in tmx_data.get_layer_by_name('Trees'):
            Tree(pos =(obj.x, obj.y), 
                 surf = obj.image, 
                 groups = [self.all_sprites, self.collision_sprites,self.tree_sprites], 
                 name = obj.name,
                 player_add = self.player_add)
      #wildflowers
         for obj in tmx_data.get_layer_by_name('Decoration'):
            WildFlower((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites])
      #collision tiles
         for x, y, surf in tmx_data.get_layer_by_name('Collision').tiles():
            Generic((x * tile_size, y * tile_size),pygame.Surface((tile_size,tile_size)),self.collision_sprites)
      #Player
       for obj in tmx_data.get_layer_by_name('Player'):
          if obj.name == 'Start':
            self.player = Player(pos = (obj.x,obj.y), 
                                 group = self.all_sprites, 
                                 collision_sprites = self.collision_sprites, 
                                 tree_sprites = self.tree_sprites, 
                                 interaction = self.interaction_sprite, 
                                 soil_layer = self.soil_layer,
                                 toggle_shop = self.toggle_shop,
                                 open_inventory = self.open_inventory)
          if obj.name == 'Bed':
             Interaction((obj.x,obj.y),(obj.width, obj.height),self.interaction_sprite, obj.name)
          if obj.name == 'Trader':
             Interaction((obj.x,obj.y),(obj.width, obj.height),self.interaction_sprite, obj.name)

       Generic(pos = (0,0),
               surf = pygame.image.load('../graphics/world/ground.png').convert_alpha(),
               groups= self.all_sprites,
               z = layers['ground'])
    
    def player_add(self,item):
       self.player.item_inventory[item] += 1
       self.success.play()

    def toggle_shop(self):
       self.shop_active = not self.shop_active

    def open_inventory(self):
       self.inventory_active = not self.inventory_active

    def reset(self):
       #plants
       self.soil_layer.update_plants()
       #soil
       self.soil_layer.remove_water()
       #randomize rain
       self.raining = randint(0,10) > 3
       self.soil_layer.raining = self.raining
       if self.raining:
          self.soil_layer.water_all()
       #apple on tree
       for tree in self.tree_sprites.sprites():
         for apple in tree.apple_sprites.sprites():
            apple.kill()
         tree.create_fruit()
         tree.regrow()
       #sky
       self.sky.start_color = [255,255,255]

    def plant_collision(self):
       if self.soil_layer.plant_sprites:
          for plant in self.soil_layer.plant_sprites.sprites():
             if plant.harvestable and plant.rect.colliderect(self.player.hitbox):
                self.player_add(plant.plant_type)
                plant.kill()
                Particle(plant.rect.topleft, plant.image, self.all_sprites, layers['main'])
                self.soil_layer.grid[plant.rect.centery // tile_size][plant.rect.centerx // tile_size].remove('P')

    def run(self,dt):
       #draw the surface & player
       self.display_surface.fill('black')
       self.all_sprites.custom_draw(self.player)
       #update
       if self.shop_active:
          self.menu.update()

       elif self.inventory_active:
          self.inventory.update()
       else:
          self.all_sprites.update(dt)
          self.plant_collision()
       #weather
       self.overlay.display()
       #rain
       if self.raining and not self.shop_active:
          self.rain.update()
       #daytime
       self.sky.display(dt)
       #transitions overlay
       if self.player.sleep:
          self.transition.play()

class CameraGroup(pygame.sprite.Group):
   def __init__(self):
      super().__init__()
      self.display_surface = pygame.display.get_surface()
      #make the camera follow the player
      self.offset = pygame.math.Vector2()

   def custom_draw(self,player):
      #how much the sprites is shifting + ensure that the player is always at the center
      self.offset.x = player.rect.centerx - screen_width/2
      self.offset.y = player.rect.centery - screen_height/2
      #make sure an image is in the right position(layer)
      for layer in layers.values():
         #make 3d effect when the player is behind or in front of an object
         for sprite in sorted(self.sprites(), key = lambda sprite : sprite.rect.centery):
            if sprite.z == layer:
               offset_rect = sprite.rect.copy()
               offset_rect.center -= self.offset
               self.display_surface.blit(sprite.image, offset_rect)
      