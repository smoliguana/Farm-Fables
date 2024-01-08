import pygame
from settings import screen_width, screen_height

class Inventory:
    def __init__(self, player, open_inventory):
        # General setup
        self.player = player
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font('../font/LycheeSoda.ttf', 30)
        # Option
        self.width = 400
        self.space = 10
        self.padding = 8
        # Toggle
        self.open_inventory = open_inventory

    def display_money(self):
        text_surf = self.font.render(f'Currency: ${self.player.money}', False, 'Brown')
        text_rect = text_surf.get_rect(midbottom=(screen_width / 2, screen_height - 40))
        pygame.draw.rect(self.display_surface, 'White', text_rect.inflate(10, 10), 0, 6)
        self.display_surface.blit(text_surf, text_rect)

    def display_inventory(self):
        title_surf = self.font.render("Inventory", False, 'Brown')
        title_rect = title_surf.get_rect(midtop=(screen_width / 2, 50))
        self.display_surface.blit(title_surf, title_rect)

        top = title_rect.bottom + 20
        for item, amount in self.player.item_inventory.items():
            text_surf = self.font.render(f'{item}: {amount}', False, 'Brown')
            bg_rect = pygame.Rect((screen_width / 2) - 150, top, 300, text_surf.get_height())
            pygame.draw.rect(self.display_surface, 'White', bg_rect, 0, 6)
            text_rect = text_surf.get_rect(center=(screen_width / 2, bg_rect.centery))
            self.display_surface.blit(text_surf, text_rect)
            top += text_surf.get_height() + 10

        for item, amount in self.player.seed_inventory.items():
            text_surf = self.font.render(f'{item}: {amount}', False, 'Brown')
            bg_rect = pygame.Rect((screen_width / 2) - 150, top, 300, text_surf.get_height())
            pygame.draw.rect(self.display_surface, 'White', bg_rect, 0, 6)
            text_rect = text_surf.get_rect(center=(screen_width / 2, bg_rect.centery))
            self.display_surface.blit(text_surf, text_rect)
            top += text_surf.get_height() + 10

    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_i] and not self.open_inventory:
            self.open_inventory()

        if keys[pygame.K_ESCAPE]:
            self.open_inventory()

    def update(self):
        self.input()
        if self.open_inventory:
            self.display_inventory()