import pygame

BG_COLOR = (255,255,255)
WIDTH, HEIGHT = 1000, 800

FPS = 60
PLAYER_VEL = 5
block_size = 96
LEVEL = 1

pygame.init()
clock = pygame.time.Clock()
pygame.display.set_caption("Platformer")
menu = pygame.display.set_mode((WIDTH, HEIGHT))

class Button:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False

        #get mouse position
        pos = pygame.mouse.get_pos()

        #check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False


        #draw button
        menu.blit(self.image, self.rect)

        return action

def draw_text(text, font, color, x, y, w):
    img = font.render(text, True, color)
    w.blit(img,(x,y))

run = True
while run:
    menu.fill((255,255,255))
    font = pygame.font.SysFont("arialblack", 40)
    draw_text("GAME OVER", font, "black",500,400,menu)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    pygame.display.update()

pygame.quit()
