import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join

pygame.init()

pygame.display.set_caption("Platformer")

BG_COLOR = (255,255,255)
WIDTH, HEIGHT = 1000, 800
FPS = 60
PLAYER_VEL = 5

window = pygame.display.set_mode((WIDTH,HEIGHT))

def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(dir1, dir2, width, height, direction = False):
    path = join("img", dir1,dir2)
    images =  [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width()//width):
            surface = pygame.Surface((width, height),pygame.SRCALPHA, 32)
            rect = pygame.Rect(i*width, 0, width, height)
            surface.blit(sprite_sheet, (0,0), rect)
            sprites.append(pygame.transform.scale2x(surface))
        
        if direction:
            all_sprites[image.replace(".png","") + "_right"] = sprites
            all_sprites[image.replace(".png","") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png","")] = sprites

    return all_sprites

def get_block(size):
    path = join("img","tile","Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size,size),pygame.SRCALPHA,32)
    rect = pygame.Rect(96,0,size,size)# sprite의 top left x,y좌표 
    surface.blit(image,(0,0),rect)

    return pygame.transform.scale2x(surface)


class Player(pygame.sprite.Sprite):
    GRAVITY = 1
    SPRITES = load_sprite_sheets("player","",32,32,True)
    ANIMATION_DELAY = 3

    def __init__(self,x,y,width,height):
        super().__init__()
        self.rect = pygame.Rect(x,y,width,height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count =  0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        
        # for health
        self.current_health = 200
        self.max_health = 200
        self.healt_bar_length = 200

        # for attack
        self.can_attack = False
        self.attack_count = 0
        self.attack_gage = 10
        self.current_attack_gage = 10

        # for skill 
        self.skill1_gage = 10
        self.current_skill1_gage = 10
        
    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    # 공격 시 애니메이션 처리 / gage관리
    def attack(self):
        self.can_attack = True
        self.animation_count = 0

    def move(self,dx,dy):
        self.rect.x += dx
        self.rect.y += dy
    
    #데미지 입기 + 애니메이션
    def make_hit(self,amount):
        self.hit_count = 0
        if self.current_health > 0:
            self.current_health -= amount
            self.hit = True
        if self.current_health <=0:
            self.current_health = 0

    #체력 회복
    def get_health(self,amount):
        if self.current_health < self.max_health:
            self.current_health += amount
        if self.current_health >= self.max_health:
            self.current_health = self.max_health

    def move_left(self,vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self,vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count/fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps:
            self.hit = False
            self.hit_count = 0

        if self.can_attack:
            self.attack_count += 1
            if self.attack_count > fps*0.2:
                self.can_attack = False
                self.attack_count = 0

        self.fall_count += 1
        self.update_sprite()
        
    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "Idle"
        if self.hit:
            sprite_sheet = "Hit"
        elif self.can_attack:
            sprite_sheet = "Attack"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "Jump"
            elif self.jump_count == 2:
                sprite_sheet = "Double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "Fall"
        elif self.x_vel != 0:
            sprite_sheet = "Run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = self.animation_count // self.ANIMATION_DELAY % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft = (self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):
        #self.sprite = self.SPRITES["Idle_"+ self.direction][0]
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))


class Enemy(pygame.sprite.Sprite):
    GRAVITY = 1
    SPRITES = load_sprite_sheets("Trunk","",64,32,True)
    ANIMATION_DELAY = 3

    def __init__(self,x,y,width,height,end):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.name = "enemy"
        self.mask = None
        self.direction = "left"
        self.path = [x,end]
        self.vel = 3
        self.animation_count = 0

        # for damage
        self.damaged = False
        self.damaged_count = 0
    

    def move(self):
        if self.vel > 0:
            self.direction = "left"
            if self.rect.x < self.path[1] + self.vel:
                self.rect.x += self.vel
            else:
                self.vel = self.vel*-1
                self.rect.x += self.vel
                self.animation_count = 0
        else:
            self.direction = "right"
            if self.rect.x > self.path[0] - self.vel:
                self.rect.x += self.vel
            else:
                self.vel  = self.vel * -1
                self.rect.x += self.vel
                self.animation_count = 0

    def update_sprite(self):
        sprite_sheet = "Idle"
        if self.vel != 0:
            sprite_sheet = "Run"
        if self.damaged:
            sprite_sheet = "Hit"
            self.vel = 0

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = self.animation_count // self.ANIMATION_DELAY % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()
    
    def update(self):
        self.rect = self.sprite.get_rect(topleft = (self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)
        
    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))

    def loop(self, fps):
        self.move()
        if self.damaged:
            self.damaged_count +=1
        if self.damaged_count > fps:
            self.damaged = False
            self.damaged_count = 0
            self.vel = 3

        self.update_sprite()
    

class Object(pygame.sprite.Sprite):
    def __init__(self, x,y,width,height, name = None):
        super().__init__()
        self.rect = pygame.Rect(x,y,width,height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name
    
    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))

class Block(Object):
    def __init__(self,x,y,size):
        super().__init__(x,y,size,size)
        block = get_block(size)
        self.image.blit(block, (0,0))
        self.mask = pygame.mask.from_surface(self.image)


# 38*38
class Saw(Object):
    ANIMATION_DELAY = 3
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "Saw")
        self.saw = load_sprite_sheets("Traps","Saw",width,height)
        self.image = self.saw["Off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "Off"

    def on(self):
        self.animation_name = "On"

    def off(self):
        self.animation_name = "Off"

    def loop(self):
        sprites = self.saw[self.animation_name]
        sprite_index = self.animation_count // self.ANIMATION_DELAY % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


class Projectile(object):
    def __init__ (self, x,y,radius,color,facing):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.facing = facing
        self.velocity = 8 * facing

    def draw(self, win, offset):
        pygame.draw.circle(win, self.color, (self.x-offset, self.y), self.radius)


class FireProjectile(Projectile):
    def __init__(self, x, y, radius, color, facing):
        super().__init__(x, y, radius, color, facing)
        self.type = "fire"
        self.damage = 10


def get_background(name):
    image = pygame.image.load(join("img", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH//width + 1):
        for j in range(HEIGHT//height + 1):
            pos = (i*width, j*height)
            tiles.append(pos)

    return tiles, image


def draw(window, background, bg_image, player, objects, offset_x, bullets, enemy1):
    for tile in background:
        window.blit(bg_image, tile)

    for object in objects:
        object.draw(window, offset_x)

    for bullet in bullets:
        bullet.draw(window, offset_x)

    pygame.draw.rect(window, (255,0,0), (10,10, player.current_health, 25))
    pygame.draw.rect(window, (255,255,255), (10,10, player.healt_bar_length, 25), 4)

    pygame.draw.rect(window, (0,0,0), (10,35, player.current_attack_gage * 20, 25))
    pygame.draw.rect(window, (255,255,255), (10,35, player.attack_gage * 20, 25), 4)

    pygame.draw.rect(window, (0,255,0), (10,60, player.current_skill1_gage * 20, 25))
    pygame.draw.rect(window, (255,255,255), (10,60, player.skill1_gage * 20, 25), 4)

    player.draw(window, offset_x)
    enemy1.draw(window, offset_x)

    pygame.display.update()



def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for object in objects:
        if pygame.sprite.collide_mask(player, object):
            if dy > 0:
                player.rect.bottom = object.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = object.rect.bottom
                player.hit_head()

            collided_objects.append(object)

    return collided_objects


def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for object in objects:
        if pygame.sprite.collide_mask(player, object):
            collided_object = object
            break

    player.move(-dx, 0)
    player.update()
    return collided_object


def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL*2)
    collide_right = collide(player, objects, PLAYER_VEL*2)

    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]
    for obj in to_check:
        if obj and obj.name == "Saw":
            player.make_hit(10)

        if obj and obj.name == "enemy":
            player.make_hit(20)


def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Yellow.png")

    block_size = 96

    player = Player(100,100,50,50)
    enemy1 = Enemy(400, HEIGHT - block_size- 64, 32, 32, 1000)

    saw = Saw(100, HEIGHT - block_size - 76, 38, 76)
    saw.on()

    #blocks = [Block(0, HEIGHT-block_size, block_size)]
    floor = [Block(i*block_size, HEIGHT - block_size, block_size) for i in range(-WIDTH//block_size, WIDTH * 2 //block_size)]

    objects = [*floor, Block(0, HEIGHT - block_size*2, block_size), Block(block_size * 3, HEIGHT - block_size*4, block_size), saw, enemy1] 

    offset_x = 0
    scroll_area_width = 200

    bullets = []
    run = True
    while(run):
        clock.tick(FPS)
        
        # for bullet    
        for b in bullets:
            if b.x > player.rect.centerx - 700 and b.x < player.rect.centerx + 700:
                b.x += b.velocity
                #print(f"{b.x}")
                #print(f"{b.y}, {enemy1.rect.centery}")
                if (b.x >= enemy1.rect.centerx-5 and b.x <= enemy1.rect.centerx + 5) and (b.y >= enemy1.rect.centery-5 and b.y <= enemy1.rect.centery + 5):
                    print(f"{enemy1.rect.x}, {b.x}")
                    enemy1.damaged = True
                    bullets.pop(bullets.index(b))
                else:
                    enemy1.damaged = False
            else:
                bullets.pop(bullets.index(b))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                # jump
                if event.key == pygame.K_s and player.jump_count < 2:
                    player.jump()

                # attack
                if event.key == pygame.K_a:
                    player.attack()
                    if player.direction == "left":
                        facing = -1
                    else:
                        facing = 1

                    if player.current_attack_gage > 0:
                        bullet = Projectile(player.rect.centerx, player.rect.centery, 6, (0,0,0), facing)                    
                        bullets.append(bullet)
                        #print(f"player : {player.rect.centerx}, {player.rect.centery}")
                        #print(f"bullet : {bullet.x}, {bullet.y}")
                        player.current_attack_gage -= 1
                    if player.current_attack_gage == 0:
                        player.can_attack = False
            
        player.loop(FPS)
        enemy1.loop(FPS)
        saw.loop()

        handle_move(player, objects)
        draw(window, background, bg_image, player,objects, offset_x, bullets, enemy1)

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or ((player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel

    pygame.quit()
    quit()

if __name__ == "__main__":
    main(window)


# 1:37:29