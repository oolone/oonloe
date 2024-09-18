import pygame

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 32)
        self.username = ''
        self.score = 0

    def run(self):
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return False

            self.screen.fill((0, 0, 0))
            text_surface = self.font.render('Game in Progress...', True, (255, 255, 255))
            self.screen.blit(text_surface, (50, 50))

        return True  # Assume victory for now
