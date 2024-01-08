import pygame
from settings import *
from support import *
import random


class Duck(pygame.sprite.Sprite):
    def __init__(self, group, player, collision_sprites):
        super().__init__(group)
        self.import_assets()
        self.status = 'down'
        self.frame_index = 0
        # General setup
        self.image = self.animations['down'][0]
        self.rect = self.image.get_rect(center=player.rect.center)
        self.z = layers['main']
        # Movement attributes
        self.direction = pygame.math.Vector2()
        self._dx = random.randint(-2, 2)
        self._dy = random.randint(-2, 2)
        # Default position on the center
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 75
        #collison
        self.collision_sprites = collision_sprites
        self.hitbox = self.rect.copy().inflate((-126,-70))

    def get_status(self):
        #check if player is idle
        if self.direction.magnitude() == 0:
            #make sure there's only 1 idle in the status
            self.status = self.status.split('_')[0] + '_idle'
    
    def input(self):
        # Change direction periodically for random movement
        if random.random() < 0.01:  # Adjust the probability as needed
            self._dx = random.randint(-2, 2)
            self._dy = random.randint(-2, 2)

        # Update status based on dx and dy
        if self._dy == -1:
            self.status = 'up'
        elif self._dy == 1:
            self.status = 'down'
        else:
            self._dy = 0

        if self._dx == -1:
            self.status = 'left'
        elif self._dx == 1:
            self.status = 'right'
        else:
            self._dx = 0

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
        # update the rect based on the new position
        self.rect.centerx = round(self.pos.x)
        self.rect.centery = round(self.pos.y)
           
    #make sure to import the right asset
    def import_assets(self):
        self.animations = {'up': [],'down': [],'left': [],'right': [],
						   'right_idle':[],'left_idle':[],'up_idle':[],'down_idle':[]}
        
        for animation in self.animations.keys():
            full_path = '../graphics/duck/' + animation
            self.animations[animation] = import_folder(full_path)

    def animate(self, dt):
        self.frame_index += 4 * dt
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0

        self.image = self.animations[self.status][int(self.frame_index)]

    def update(self, dt):
        self.input()
        self.get_status()
        self.move(dt)
        self.animate(dt)
