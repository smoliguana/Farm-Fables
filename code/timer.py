import pygame

class Timer:
    def __init__(self,duration,func = None):
        self.duration = duration
        self.func = func
        self.start_time = 0 
        self.active = False

    def activate(self):
        self.active = True
        #check when is the start time
        self.start_time = pygame.time.get_ticks()

    def deactivate(self):
        self.active = False
        self.start_time = 0

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time >= self.duration:
            #call the function if it exists
            #(!=) different than
            if self.func and self.start_time !=0:
                self.func()
            self.deactivate()
            