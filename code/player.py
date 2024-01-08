import pygame
from settings import *
from support import *
from timer import Timer

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group, collision_sprites, tree_sprites, interaction, soil_layer, toggle_shop, open_inventory):
        super().__init__(group)
        #import assets
        self.import_assets()
        self.status = 'down_idle'
        self.frame_index = 0
        # General setup
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center = pos)
        self.z = layers['main']
        # Movement attributes
        self.direction = pygame.math.Vector2()
        # Default position on the center
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 200
        #collison
        self.collision_sprites = collision_sprites
        self.hitbox = self.rect.copy().inflate((-126,-70))
        #timer
        self.timers = {
            'tool use': Timer(350,self.use_tool),
            'tool switch': Timer(200),
            'seed use': Timer(350,self.use_seed),
            'seed switch': Timer(200)
        }
        #tools
        self.tools = ['hoe', 'axe', 'water']
        self.tool_index = 0
        self.selected_tool = self.tools[self.tool_index]
        #seeds
        self.seeds = ['corn', 'tomato']
        self.seed_index = 0
        self.selected_seed = self.seeds[self.seed_index]
        #inventory
        self.item_inventory = {
            'wood': 0,
            'apple': 0,
            'corn': 0,
            'tomato': 0
        }
        #seed inventory
        self.seed_inventory = {
            '(s)corn': 5,
            '(s)tomato': 5
        }
        self.money = 100
        #interaction
        self.tree_sprites = tree_sprites
        self.interaction = interaction
        self.sleep = False
        self.soil_layer = soil_layer
        self.toggle_shop = toggle_shop
        #inventory
        self.open_inventory = open_inventory
        #sfx
        self.watering = pygame.mixer.Sound('../audio/water.mp3')
        self.watering.set_volume(0.2)

    def use_tool(self):
        if self.selected_tool == 'hoe':
            self.soil_layer.get_hit(self.target_pos)
        if self.selected_tool == 'axe':
            for tree in self.tree_sprites.sprites():
                if tree.rect.collidepoint(self.target_pos):
                    tree.damage()
        if self.selected_tool == 'water':
            self.soil_layer.water(self.target_pos)
            self.watering.play()

    def get_target_pos(self):
        self.target_pos = self.rect.center + player_tool_offset[self.status.split('_')[0]]

    def use_seed(self):
        if self.seed_inventory[self.selected_seed] > 0:
            self.soil_layer.plant_seed(self.target_pos, self.selected_seed)
            self.seed_inventory[self.selected_seed] -= 1

    #make sure to import the right asset
    def import_assets(self):
        self.animations = {'up': [],'down': [],'left': [],'right': [],
						   'right_idle':[],'left_idle':[],'up_idle':[],'down_idle':[],
						   'right_hoe':[],'left_hoe':[],'up_hoe':[],'down_hoe':[],
						   'right_axe':[],'left_axe':[],'up_axe':[],'down_axe':[],
						   'right_water':[],'left_water':[],'up_water':[],'down_water':[]}
        
        for animation in self.animations.keys():
            full_path = '../graphics/character/' + animation
            self.animations[animation] = import_folder(full_path)

    #make the image animate
    def animate(self,dt):
        self.frame_index += 4 * dt
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0

        self.image = self.animations[self.status][int(self.frame_index)]

    
    def input(self):
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        if not self.timers['tool use'].active and not self.sleep:
            #direction input
            # Vertical axis
            if keys[pygame.K_UP]:
                self.direction.y = -1
                self.status = 'up'
            elif keys[pygame.K_DOWN]:
                self.direction.y = 1
                self.status = 'down'
            else:
                self.direction.y = 0
            # Horizontal axis
            if keys[pygame.K_RIGHT]:
                self.direction.x = 1
                self.status = 'right'
            elif keys[pygame.K_LEFT]:
                self.direction.x = -1
                self.status = 'left'
            else:
                self.direction.x = 0
            #tool use
            if keys[pygame.K_SPACE]:
                #timer for tool use
                self.timers['tool use'].activate()
                self.direction = pygame.math.Vector2()
                #making sure the frame starts at 0
                self.frame_index = 0
            #changing tools
            #make the output a single number(the img file is a number from 0-3)
            if keys[pygame.K_q] and not self.timers['tool switch'].active:
                self.timers['tool switch'].activate()
                #go through the tool dict to access each tool
                self.tool_index += 1
                #loop through the len of tools
                if self.tool_index < len(self.tools):
                    self.tool_index = self.tool_index
                else : 
                    self.tool_index = 0
                self.selected_tool = self.tools[self.tool_index]

            #seed use
            if keys[pygame.K_LSHIFT]:
                #timer for seed use
                self.timers['seed use'].activate()
                self.direction = pygame.math.Vector2()
                #making sure the frame starts at 0
                self.frame_index = 0
            #changing seeds
            #make the output a single number(the img file is a number from 0-3)
            if keys[pygame.K_w] and not self.timers['seed switch'].active:
                self.timers['seed switch'].activate()
                #go through the seed dict to access each tool
                self.seed_index += 1
                #loop through the len of tools
                if self.seed_index < len(self.seeds):
                    self.seed_index = self.seed_index
                else : 
                    self.seed_index = 0
                self.selected_seed = self.seeds[self.seed_index]  
            #restart day & trader
            if keys[pygame.K_RETURN]:
                collided_interaction_sprite = pygame.sprite.spritecollide(self, self.interaction,False)
                if collided_interaction_sprite:
                    if collided_interaction_sprite[0].name == 'Trader':
                        self.toggle_shop()
                    else:
                        self.status = 'left_idle'
                        self.sleep = True
            #open inventory
            if keys[pygame.K_i]:
                self.open_inventory()


    def get_status(self):
        #check if player is idle
        if self.direction.magnitude() == 0:
            #make sure there's only 1 idle in the status
            self.status = self.status.split('_')[0] + '_idle'
            #using tools
        if self.timers['tool use'].active:
            self.status = self.status.split('_')[0] + '_' + self.selected_tool
    #make sure to not loop the tool use forever
    
    def update_timers(self):
        for timer in self.timers.values():
            timer.update()
    
    def collision(self, direction):
        for sprite in self.collision_sprites.sprites():
            if hasattr(sprite, 'hitbox'):
                if sprite.hitbox.colliderect(self.hitbox):
                    if direction == 'horizontal':
                        if self.direction.x > 0: #moving right(basically the collision is coming frpm the left direction)
                            self.hitbox.right = sprite.hitbox.left
                        if self.direction.x < 0: #moving left(collision from right)
                            self.hitbox.left = sprite.hitbox.right
                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx
                    if direction == 'vertical':
                        if self.direction.y > 0: #moving down(collision from up)
                            self.hitbox.bottom = sprite.hitbox.top
                        if self.direction.y < 0: #moving up(collision from down)
                            self.hitbox.top = sprite.hitbox.bottom
                        self.rect.centery = self.hitbox.centery
                        self.pos.y = self.hitbox.centery

    def move(self, dt):
        #normalizing vector(make sure the speed is consistent)
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()
        
        #horizontal movement
        self.pos.x += self.direction.x * self.speed * dt
        #round up the value to prevent errors
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')

        #vertical movement
        self.pos.y += self.direction.y * self.speed * dt
        #round up the value to prevent errors
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision('vertical')

    #update the game based on the input given(VERY IMPORTANT, CHECK CONSTANTLY)
    def update(self, dt):
        self.input()
        self.get_status()
        self.update_timers()
        self.get_target_pos()

        self.move(dt)
        self.animate(dt) 
