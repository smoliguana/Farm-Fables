from os import walk
import os.path
import pygame

def import_folder(path):
    # Turn the contents of the folder into a list of surfaces
    surface_list = []
    
    for _, __, img_files in walk(path):
        for image in img_files:
            full_path = path + '/' + image
            
            # Load image and convert to surface
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surf)

    return surface_list

def import_folder_dict(path):
    surface_dict = {}
    for _, __, img_files in walk(path):
        for image in img_files:
            full_path = path + '/' + image
            
            # Load image and convert to surface
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_dict[image.split('.')[0]] = image_surf
    return surface_dict