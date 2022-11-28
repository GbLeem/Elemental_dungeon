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
        self.attack_gage = 20
        self.current_attack_gage = 20

        # for skill 
        self.skill1_gage = 10
        self.current_skill1_gage = 10
        self.skill2_gage = 10
        self.current_skill2_gage = 10
        self.skill3_gage = 10
        self.current_skill3_gage = 10
        
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
    
    def death(self):
        pass

    #데미지 입기 + 애니메이션
    def make_hit(self,amount):
        self.hit_count = 0
        if self.current_health > 0:
            self.current_health -= amount
            self.hit = True
        if self.current_health <=0:
            self.current_health = 0
            self.death()

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
        # 죽는 것 구현하는 부분
        elif self.current_health <= 0:
            sprite_sheet = "Die"
            #한번만 보여주고 끝나기 추가하기
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

#======================================Enemy====================================================================
class Enemy(object):
    GRAVITY = 1
    SPRITES = load_sprite_sheets("Trunk","",64,32,True)
    ANIMATION_DELAY = 3

    def __init__(self,x,y,width,height,end, elemental):
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
        self.elemental = elemental

        # health
        self.health = 10

        # for death
        self.visible = True

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

    def dead(self):
        self.visible = False
        self.rect = pygame.Rect(0,0, 0,0) # for collision ending

    # def attack_player(self):
    #     pass

    # def hit(self):
    #     pass
    
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
        if self.visible:
            win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))
    
    def loop(self, fps):
        self.move()
        if self.damaged:
            self.damaged_count +=1
        if self.damaged_count > fps:
            self.damaged = False
            self.damaged_count = 0
            self.vel = 3
        if self.health <= 0:
            self.dead()
        self.update_sprite()


# 36*30
class FireEnemy(object):
    GRAVITY = 1
    SPRITES = load_sprite_sheets("AngryPig","",36, 30,True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height, end, elemental):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.name = "enemy"
        self.mask = None
        self.direction = "left"
        self.path = [x, end]
        self.vel = 3
        self.animation_count = 0

        # for damage
        self.damaged = False
        self.damaged_count = 0
        self.elemental = elemental

        # health
        self.health = 20

        # for death
        self.visible = True

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

    def dead(self):
        self.visible = False
        self.rect = pygame.Rect(0,0, 0,0) # for collision ending

    def update_sprite(self):
        #super().update_sprite()
        sprite_sheet = "Run"
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
        if self.visible:
            win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))

    def loop(self, fps):
        self.move()
        if self.damaged:
            self.damaged_count += 1
        if self.damaged_count > fps:
            self.damaged = False
            self.damaged_count = 0
            self.vel = 3
        if self.health <= 0:
            self.dead()
        self.update_sprite()


# 32*32
class WaterBird(Enemy):
    GRAVITY = 1
    SPRITES = load_sprite_sheets("BlueBird","",32, 30,True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height, end, elemental):
        super().__init__(x, y, width, height, end, elemental)
        self.rect = pygame.Rect(x, y, width, height)
        self.name = "enemy"
        self.mask = None
        self.direction = "left"
        self.path = [x, end]
        self.vel = 3
        self.animation_count = 0

        # for damage
        self.damaged = False
        self.damaged_count = 0
        self.elemental = elemental

        # health
        self.health = 5

        # for death
        self.visible = True

    def update_sprite(self):
        #super().update_sprite()
        sprite_sheet = "Flying"
        if self.vel != 0:
            sprite_sheet = "Flying"
        if self.damaged:
            sprite_sheet = "Hit"
            self.vel = 0

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = self.animation_count // self.ANIMATION_DELAY % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def loop(self, fps):
        self.move()
        if self.damaged:
            self.damaged_count +=1
        if self.damaged_count > fps*0.3:
            self.damaged = False
            self.damaged_count = 0
            self.vel = 3
        if self.health <= 0:
            self.dead()
        self.update_sprite()

# 34*44
class FireBunny(Enemy):
    GRAVITY = 1
    SPRITES = load_sprite_sheets("Bunny","",34, 44,True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height, end, elemental):
        super().__init__(x, y, width, height, end, elemental)
        self.rect = pygame.Rect(x, y, width, height)
        self.name = "enemy"
        self.mask = None
        self.direction = "left"
        self.path = [x, end]
        self.vel = 3
        self.animation_count = 0

        self.health = 5

    def update_sprite(self):
        sprite_sheet = "Run"
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
#======================================Enemy====================================================================

#======================================BOSS====================================================================
# 250 * 250
class BOSS(Enemy):
    GRAVITY = 1
    SPRITES = load_sprite_sheets("Boss","",250, 250,True)
    ANIMATION_DELAY = 5

    def __init__(self, x, y, width, height, end, elemental):
        super().__init__(x, y, width, height, end, elemental)
        self.rect = pygame.Rect(x, y, width, height)
        self.name = "enemy"
        self.mask = None
        self.direction = "left"
        self.path = [x, end]
        self.vel = 2
        self.animation_count = 0
        self.health = 5
        
        #for attack
        self.can_attack = False 

    def attack(self):
        self.can_attack = True
        self.animation_count = 0

    def update_sprite(self):
        sprite_sheet = "Idle"
        if self.vel != 0:
            sprite_sheet = "Run"
        if self.damaged:
            sprite_sheet = "Hit"
            self.vel = 0
        if self.can_attack:
            sprite_sheet = "Attack1"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = self.animation_count // self.ANIMATION_DELAY % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()


    def loop(self, fps):
        self.move()
        if self.damaged:
            self.damaged_count +=1

        if self.damaged_count > fps*0.3:
            self.damaged = False
            self.damaged_count = 0
            self.vel = 3

        if self.health <= 0:
            self.dead()

        if self.can_attack:
            self.attack_count += 1
            if self.attack_count > fps*0.2:
                self.can_attack = False
                self.attack_count = 0

        self.update_sprite()


#======================================BOSS====================================================================




class Elements(object):
    def __init__(self, x,y, width, color):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.color = color        
    
    def draw(self,win,offset_x):
        pygame.draw.rect(win, self.color, (self.x-offset_x, self.y, self.width, self.width))

#======================================Block and obstacle=======================================================
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

# 42*42
class RockHead(Object):
    ANIMATION_DELAY = 10
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "RockHead")
        self.rockhead = load_sprite_sheets("Traps","RockHead",width,height)
        self.image = self.rockhead["Blink"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "Blink"

        #for move
        self.path = [y,HEIGHT - 96 - 42]
        self.vel = 10
        self.delaytime = 0
        self.direction = "up"

    def Fall(self):
        self.animation_name = "BottomHit"

    def Idle(self):
        self.animation_name = "Blink"

    def move(self):
        if self.vel > 0:
            self.direction = "down"
            self.Fall()
            if self.rect.y+42 < self.path[1] + self.vel:
                self.rect.y += self.vel
            else:
                self.vel = self.vel*-1
                self.rect.y += self.vel
                self.animation_count = 0
        else:
            self.direction = "up"
            self.Idle()
            if self.rect.y > self.path[0] - self.vel:
                self.rect.y += self.vel
            else:
                self.vel  = self.vel * -1
                self.rect.y += self.vel
                self.animation_count = 0

    def loop(self,fps):
        self.move()
        sprites = self.rockhead[self.animation_name]
        sprite_index = self.animation_count // self.ANIMATION_DELAY % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0
    
        # for move obstacle
        # if self.delaytime < fps:
        #     self.delaytime += 1
        # if self.delaytime > fps:
        #     self.delaytime = 0

class HealthItem(Object):
    ANIMATION_DELAY = 3
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "Melon")
        self.melon = load_sprite_sheets("Items","Fruits",width, height)
        self.image = self.melon["Melon"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "Melon"

    def idle(self):
        self.animation_name = "Melon"

    def loop(self):
        sprites = self.melon[self.animation_name]
        sprite_index = self.animation_count // self.ANIMATION_DELAY % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1
        self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)
        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

        
#=========================================Block and obstacle====================================================

#=========================================Projectile and Skill====================================================
class Projectile(object):
    BULLETS = []
    def __init__ (self, x,y,radius,color,facing):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.facing = facing
        self.velocity = 8 * facing

    def draw(self, win, offset):
        pygame.draw.circle(win, self.color, (self.x-offset, self.y), self.radius)
#=========================================Projectile and Skill====================================================

#=========================================global function====================================================
def get_background(name):
    image = pygame.image.load(join("img", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH//width + 1):
        for j in range(HEIGHT//height + 1):
            pos = (i*width, j*height)
            tiles.append(pos)

    return tiles, image


def draw(window, background, bg_image, player, objects, offset_x, bullets,elements, enemys):
    for tile in background:
        window.blit(bg_image, tile)

    for object in objects:
        object.draw(window, offset_x)

    for bullet in bullets:
        bullet.draw(window, offset_x)

    for element in elements:
        element.draw(window, offset_x)

    for enemy in enemys:
        enemy.draw(window,offset_x)

    # health gage
    pygame.draw.rect(window, (255,0,0), (10,10, player.current_health, 25))
    pygame.draw.rect(window, (255,255,255), (10,10, player.healt_bar_length, 25), 4)

    # normal attack
    pygame.draw.rect(window, (0,0,0), (10,35, player.current_attack_gage * 20, 25))
    pygame.draw.rect(window, (255,255,255), (10,35, player.attack_gage * 20, 25), 4)

    # grass 
    pygame.draw.rect(window, (0,255,0), (10,60, player.current_skill1_gage * 20, 25))
    pygame.draw.rect(window, (255,255,255), (10,60, player.skill1_gage * 20, 25), 4)

    # fire
    pygame.draw.rect(window, (200,100,0), (10,85, player.current_skill2_gage * 20, 25))
    pygame.draw.rect(window, (255,255,255), (10,85, player.skill2_gage * 20, 25), 4)

    # water
    pygame.draw.rect(window, (0,0,255), (10,110, player.current_skill3_gage * 20, 25))
    pygame.draw.rect(window, (255,255,255), (10,110, player.skill3_gage * 20, 25), 4)

    player.draw(window, offset_x)
    #enemy1.draw(window, offset_x)
    #enemy2.draw(window, offset_x)

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

        if obj and obj.name == "RockHead":
            player.make_hit(10)
        
        if obj and obj.name == "Melon":
            player.get_health(10)


def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Yellow.png")

    block_size = 96

    player = Player(100,100,50,50)

    enemy1 = Enemy(400, HEIGHT - block_size- 64, 32, 32, 700, "grass")
    enemy2 = FireEnemy(1000, HEIGHT - block_size - 36-18, 32,30, 1000+400, "fire")
    enemy3 = WaterBird(200, HEIGHT - block_size*4-32, 32, 32, 400+100,"water")
    enemy4 = FireBunny(96, HEIGHT - block_size - 34*2-17, 32, 32, 196,"fire")

    boss = BOSS(1400, HEIGHT - block_size - 250 - 32, 32, 32, 1400 + 500, "fire")

    enemys = [enemy1,enemy2,enemy3,enemy4,boss]


    # enemys.append(enemy1)
    # enemys.append(enemy2)

    saw = Saw(96*10, HEIGHT - block_size - 76, 38, 76)
    saw.on()

    rock_head = RockHead(400, HEIGHT - block_size - 42*10, 42, 42)
    rock_head.Idle()

    # 아이템 리스트에 넣고 관리하기
    items = []
    health_item01 = HealthItem(block_size * 3, HEIGHT - block_size*4 -32- 16 , 32, 32)
    health_item01.idle()
    items.append(health_item01)

    #blocks = [Block(0, HEIGHT-block_size, block_size)]
    floor = [Block(i*block_size, HEIGHT - block_size, block_size) for i in range(-WIDTH//block_size, WIDTH * 2 //block_size)]

    objects = [*floor, Block(-block_size, HEIGHT - block_size*3, block_size) ,Block(0, HEIGHT - block_size*2, block_size), Block(block_size * 3, HEIGHT - block_size*4, block_size), 
                saw, rock_head, health_item01, enemys[0],enemys[1],enemys[2], enemys[3]] 

    offset_x = 0
    scroll_area_width = 200

    bullets = []
    elements = [] # for increase skill gage / but now for ammo

    element_draw_count = 0

    run = True

    while(run):
        clock.tick(FPS)
        
        for b in bullets:
            if b.x > player.rect.centerx - 700 and b.x < player.rect.centerx + 700:
                b.x += b.velocity
                for i in range(len(enemys)):
                    if (b.x >= enemys[i].rect.centerx-10 and b.x <= enemys[i].rect.centerx + 10) and (b.y >= enemys[i].rect.centery-10 and b.y <= enemys[i].rect.centery + 10):
                        if bullet.color == "red":
                            if enemys[i].elemental == "grass":
                                enemys[i].health -= 4
                            elif enemys[i].elemental == "water":
                                enemys[i].health -= 1
                        elif bullet.color == "green":
                            if enemys[i].elemental == "water":
                                enemys[i].health -= 4
                            elif enemys[i].elemental == "fire":
                                enemys[i].health -= 1
                        elif bullet.color == "blue":
                            if enemys[i].elemental == "fire":
                                enemys[i].health -= 4
                            elif enemys[i].elemental == "grass":
                                enemys[i].health -= 1
                        else:
                            enemys[i].health -= 2 # bullet 이랑 skill damage를 적용해야 함!! 지금은 그냥 임시 숫자임
                        
                        enemys[i].damaged = True
                        bullets.pop(bullets.index(b))
                    else:
                        enemys[i].damaged = False
            else:
                bullets.pop(bullets.index(b))


        # getting item
        for e in elements:
            if (player.rect.centerx >= e.x-5 and player.rect.centerx <= e.x+5) and (player.rect.centery >= e.y-5 and player.rect.centery <= e.y+5):
            #if player.rect.centerx == e.x:
                if e.color == "green":
                    player.current_skill1_gage += 5
                elif e.color == "red":
                    player.current_skill2_gage += 5
                elif e.color == "blue":
                    player.current_skill3_gage += 5

                player.current_attack_gage += 5
                elements.pop(elements.index(e))

                # gage 넘어가지 않게 처리
                if player.current_attack_gage > 20:
                    player.current_attack_gage = 20


        # item spawn => 한번씩만 만들어야함!
        for i in range(len(enemys)):
            if enemys[i].health <= 0:
                if element_draw_count == 0:
                    if enemys[i].elemental == "grass":
                        element = Elements(enemys[i].rect.centerx, HEIGHT - block_size - 30, 30, "green")
                    if enemys[i].elemental == "fire":
                        element = Elements(enemys[i].rect.centerx, HEIGHT - block_size - 30, 30, "red")
                    if enemys[i].elemental == "water":
                        element = Elements(enemys[i].rect.centerx, HEIGHT - block_size - 30, 30, "blue")

                    elements.append(element)


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
                        player.current_attack_gage -= 1
                    if player.current_attack_gage == 0:
                        player.can_attack = False
                
                # skill1 grass
                if event.key == pygame.K_q:
                    player.attack()
                    if player.direction == "left":
                        facing = -1
                    else:
                        facing = 1

                    if player.current_skill1_gage > 0:
                        bullet = Projectile(player.rect.centerx, player.rect.centery, 6, "green", facing)                    
                        bullets.append(bullet)
                        player.current_skill1_gage -= 1
                    if player.current_skill1_gage == 0:
                        player.can_attack = False

                # skill2 fire
                if event.key == pygame.K_w:
                    player.attack()
                    if player.direction == "left":
                        facing = -1
                    else:
                        facing = 1
                    if player.current_skill2_gage > 0:
                        bullet = Projectile(player.rect.centerx, player.rect.centery, 6, "red", facing)                    
                        bullets.append(bullet)
                        player.current_skill2_gage -= 1
                    if player.current_skill2_gage == 0:
                        player.can_attack = False
                
                # skill3 water
                if event.key == pygame.K_e:
                    player.attack()
                    if player.direction == "left":
                        facing = -1
                    else:
                        facing = 1
                    if player.current_skill3_gage > 0:
                        bullet = Projectile(player.rect.centerx, player.rect.centery, 6, "blue", facing)                    
                        bullets.append(bullet)
                        player.current_skill3_gage -= 1
                    if player.current_skill3_gage == 0:
                        player.can_attack = False
        
        player.loop(FPS)
        enemys[0].loop(FPS)
        enemys[1].loop(FPS)
        enemys[2].loop(FPS)
        enemys[3].loop(FPS)
        enemys[4].loop(FPS)

        saw.loop()
        rock_head.loop(FPS)
        health_item01.loop()
        handle_move(player, objects)
        
        draw(window, background, bg_image, player,objects, offset_x,elements, bullets, enemys)

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or ((player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel

    pygame.quit()
    quit()

if __name__ == "__main__":
    main(window)


# 1:37:29