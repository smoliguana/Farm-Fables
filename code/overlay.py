import pygame
from settings import *

class Overlay:
    def __init__(self,player):
        #general setup
        self.display_surface = pygame.display.get_surface()
        self.player = player
        #imports
        overlay_path = '../graphics/overlay/'
        frame_path = '../graphics/frame.png'
        self.frame_surf = pygame.image.load(frame_path).convert_alpha()
        self.tools_surf = {tool:pygame.image.load(f'{overlay_path}{tool}.png').convert_alpha() 
                           for tool in player.tools}
        self.seeds_surf = {seed:pygame.image.load(f'{overlay_path}{seed}.png').convert_alpha() 
                           for seed in player.seeds}
        
    def display(self):
        #frame
        frame_surf = self.frame_surf
        frame_rect = frame_surf.get_rect(topleft = (0,0))
        self.display_surface.blit(frame_surf, frame_rect)
        #tools
        tool_surf = self.tools_surf[self.player.selected_tool]
        tool_rect = tool_surf.get_rect(midbottom = overlay_positions['tool'])
        self.display_surface.blit(tool_surf,tool_rect)
        #seeds
        seed_surf = self.seeds_surf[self.player.selected_seed]
        seed_rect = seed_surf.get_rect(midbottom = overlay_positions['seed'])
        self.display_surface.blit(seed_surf,seed_rect)