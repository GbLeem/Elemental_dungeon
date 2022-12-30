from random import *
import pygame
from os import listdir
from os.path import isfile, join

pygame.init()
clock = pygame.time.Clock()
FPS = 60
WIDTH, HEIGHT = 1000, 800
PLAYER_VEL = 5
block_size = 96
game_level = 1

window = pygame.display.set_mode((WIDTH, HEIGHT))
window2 = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("Elemental Dungeon")

game_over = 1
main_menu = True

# for button images
restart_img = pygame.image.load('ui/restart_btn.png')
start_img = pygame.image.load('ui/start_btn.png')
exit_img = pygame.image.load('ui/exit_btn.png')


#================================================global function================================================

def draw_text(text, font, text_col, x, y, w):
    img = font.render(text, True, text_col)
    w.blit(img,(x,y))


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

def get_block(size, level):
    path = join("img","tile","Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size,size),pygame.SRCALPHA,32)
    if level == 1:
        rect = pygame.Rect(96,0,size,size)# sprite의 top left x,y좌표 
    elif level == 2:
        rect = pygame.Rect(96,64,size,size)
    surface.blit(image,(0,0),rect)

    return pygame.transform.scale2x(surface)

def get_background(name):
    image = pygame.image.load(join("img", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH//width + 1):
        for j in range(HEIGHT//height + 1):
            pos = (i*width, j*height)
            tiles.append(pos)

    return tiles, image



#================================================for main menu================================================
class Button:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False

        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        window.blit(self.image, self.rect)

        return action
#================================================player class================================================
class Player(pygame.sprite.Sprite):
    GRAVITY = 1
    SPRITES = load_sprite_sheets("player","",32,32,True)
    ANIMATION_DELAY = 3

    def __init__(self,x,y,width,height):
        super().__init__()
        self.reset(x,y,width,height)

    #def __init__(self,x,y,width,height):
    def reset(self,x,y,width,height):
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

        # death
        self.live = True

        # for attack
        self.can_attack = False
        self.attack_count = 0
        self.attack_gage = 20
        self.current_attack_gage = 20

        # for skill 
        self.skill1_gage = 10
        self.current_skill1_gage = 5
        self.skill2_gage = 10
        self.current_skill2_gage = 5
        self.skill3_gage = 10
        self.current_skill3_gage = 5

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
            self.live = False
        
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

    def loop(self, fps, game_over):
        if game_over == 0:
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

            if self.current_health <= 0:
                #game_scene()
                game_over = -1    

        return game_over
        
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
        #if self.live:
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
        self.rect = pygame.Rect(0, 0, 0, 0) # for collision ending
    
    def update_sprite(self):
        if self.visible:
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
        if self.visible:
            self.rect = self.sprite.get_rect(topleft = (self.rect.x, self.rect.y))
            self.mask = pygame.mask.from_surface(self.sprite)
        
    def draw(self, win, offset_x):
        if self.visible:
            win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))
    
    def loop(self, fps):
        if self.visible:
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

# 30*38
class GrassRadish(Enemy):
    GRAVITY = 1
    SPRITES = load_sprite_sheets("Radish","",30, 38,True)
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

# 44*26
class WaterTurtle(Enemy):
    GRAVITY = 1
    SPRITES = load_sprite_sheets("Turtle","",44, 26,True)
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
        self.health = 10

    def update_sprite(self):
        sprite_sheet = "Idle"
        if self.vel != 0:
            sprite_sheet = "Idle"
        if self.damaged:
            sprite_sheet = "Hit"
            self.vel = 0

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = self.animation_count // self.ANIMATION_DELAY % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()
#======================================BOSS====================================================================
# 250 * 250
class BOSS(Enemy):
    GRAVITY = 1
    SPRITES = load_sprite_sheets("Boss","",250, 250,True)
    ANIMATION_DELAY = 5

    def __init__(self, x, y, width, height, end, elemental):
        super().__init__(x, y, width, height, end, elemental)
        self.rect = pygame.Rect(x, y, width, height)
        self.name = "boss"
        self.mask = None
        self.direction = "left"
        self.path = [x, end]
        self.vel = 2
        self.animation_count = 0
        self.health = 20 # 체력
        
        #for attack
        self.attack_count1 = 0
        self.attack_count2 = 0
        self.can_attack1 = False 
        self.can_attack2 = False 
        self.attack1_gage = 0 # 약한 공격
        self.attack2_gage = 0 # 강한 공격
        self.attack3_gage = 0 # 분노 공격
        self.elemental_change = 0

        #for skill
        self.bossbulletcnt = []
        self.bossskillcnt = []

        # death
        self.death = False
        self.death_count = 0

    def attack(self):
        self.can_attack = True
        self.animation_count = 0

    def make_bullet(self):
        for i in range(10):
            bossbullet = Projectile(self.rect.centerx, self.rect.centery, 10, (0,0,0), facing)
            self.bossbulletcnt.append(bossbullet)
        return self.bossbulletcnt

    def make_skill(self):
        for i in range(20):
            randx = randint(0, WIDTH)
            bossskill = Projectile(randx, 0, 20, (255,255,255), 1)
            self.bossskillcnt.append(bossskill)
        return self.bossskillcnt

    def update_sprite(self):
        sprite_sheet = "Idle"
        if self.vel != 0:
            sprite_sheet = "Run"
        if self.damaged:
            sprite_sheet = "Hit"
            self.vel = 0
        if self.can_attack1: #약한 공격
            sprite_sheet = "Attack1"
            self.vel = 0
        if self.can_attack2: #강한 공격
            sprite_sheet = "Attack2"        
            self.vel = 0
        if self.death:
            sprite_sheet = "Death"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = self.animation_count // self.ANIMATION_DELAY % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def weak_attack(self):
        print("weak")
        self.attack1_gage = 0

    def strong_attack(self):
        print("strong")
        self.attack2_gage = 0

    def mad_attack(self):
        #print("분노 공격!!") 이때는 속성이 자주 바뀜
        self.attack3_gage = 0


    def change_mode(self):
        rnum = randint(1,4)
        if rnum == 1:
            self.elemental = "grass"
        elif rnum == 2:
            self.elemental = "fire"
        elif rnum == 3:
            self.elemental = "water"
        print(f"elemental Change!! to {self.elemental}")
        #text = f"{self.elemental}"
        #draw_text(text+" modes", "black",400, 400, window)
        self.elemental_change = 0


    def loop(self, fps):
        self.move()
        self.elemental_change += 1 #속성 바꾸기
        self.attack1_gage += 1
        self.attack2_gage += 1
        self.attack3_gage += 1   

        if self.damaged:
            self.damaged_count +=1

        if self.damaged_count > fps*0.3:
            self.damaged = False
            self.damaged_count = 0
            self.vel = 3

        if self.health <= 0:
            self.death = True
            self.death_count += 1
            if self.death_count > fps*0.3:
                self.death = False
                game_scene("GAME CLEAR")
                print("DONE")
                
        # 보스 속성 바꾸기
        if self.elemental_change > fps * 10:
            self.change_mode()

        # 보스 투사체 공격-약함
        if self.attack1_gage > fps * 4:
            #self.weak_attack()
            self.can_attack1 = True
        
        # 보스 투사체 공격-강함
        if self.attack2_gage > fps * 10:
            #self.strong_attack()
            self.can_attack2 = True

        # 분노 모드
        if self.health <= 5:
            self.attack3_gage = 1
            if self.elemental_change > fps*2:
                self.change_mode()
 
        if self.can_attack1:
            self.attack_count1 += 1
            if self.attack_count1 > fps*1:
                self.can_attack1 = False
                self.attack1_gage = 0
                self.attack_count1 = 0
                self.vel = 2

        if self.can_attack2:
            self.attack_count2 += 1
            if self.attack_count2 > fps*1.5:
                self.can_attack2 = False
                self.attack2_gage = 0
                self.attack_count2 = 0
                self.vel = 2


        self.update_sprite()
#=========================================Projectile class===================================================
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

class Elements(object):
    def __init__(self, x,y, width, color):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.color = color        
    
    def draw(self,win,offset_x):
        pygame.draw.rect(win, self.color, (self.x-offset_x, self.y, self.width, self.width))
#================================================Object================================================
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
    def __init__(self,x,y,size,level):
        super().__init__(x,y,size,size)
        block = get_block(size,level)
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
        self.path = [y, HEIGHT - 96 - 42]
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

    def loop(self):
        self.move()
        sprites = self.rockhead[self.animation_name]
        sprite_index = self.animation_count // self.ANIMATION_DELAY % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

class HealthItem(Object):
    ANIMATION_DELAY = 3
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "Melon")
        self.melon = load_sprite_sheets("Items","Fruits",width, height)
        self.image = self.melon["Melon"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "Melon"
        self.eat = False

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

# 46*56
class FinalZone(Object):
    ANIMATION_DELAY = 3
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "final")
        self.final = load_sprite_sheets("Items","Door",width, height)
        self.image = self.final["Opening"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "Opening"

    def idle(self):
        self.animation_name = "Opening"

    def loop(self):
        sprites = self.final[self.animation_name]
        sprite_index = self.animation_count // self.ANIMATION_DELAY % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1
        self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)
        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0
#================================================make level================================================
def make_level_1():
    background, bg_image = get_background("Yellow.png")
    sound = pygame.mixer.Sound("music/xDeviruchi - Minigame .wav")

    # 0~1000 / 1000 ~ 2000 / 2000 ~ 3000 / 3000 ~ 4000
    enemy1 = Enemy(400, HEIGHT - block_size- 64, 32, 32, 400+150, "grass")
    enemy2 = GrassRadish(700, HEIGHT- block_size-38*2, 32, 32, 700+300,"grass")
    enemy3 = GrassRadish(800, HEIGHT- block_size-38*2, 32, 32, 800+200,"grass")

    enemy4 = FireEnemy(1200, HEIGHT - block_size - 36-18, 32,30, 1200+100, "fire")
    enemy5 = FireBunny(1800, HEIGHT - block_size - 34*2-17, 32, 32, 1800+170,"fire")
    enemy6 = FireBunny(2200, HEIGHT - block_size - 34*2-17, 32, 32, 2200+200,"fire")
    enemy7 = FireEnemy(2500, HEIGHT - block_size - 36-18, 32,30, 2500+200, "fire")

    enemy8 = WaterBird(2600, HEIGHT - block_size*4, 32, 32, 2600+100,"water")
    enemy9 = WaterTurtle(2800,HEIGHT - block_size- 26*2, 32, 32, 2800+300,"water")
    enemy10 = WaterBird(3300, HEIGHT - block_size*4-32, 32, 32, 3300+200,"water")


    enemys = [enemy1,enemy2,enemy3,enemy4,enemy5,enemy6,enemy7,enemy8,enemy9,enemy10]

    saw = Saw(2500, HEIGHT - block_size - 76, 38, 76)
    saw.on()
    saw2 = Saw(1100, HEIGHT - block_size - 76, 38, 76)
    saw2.on()


    rock_head = RockHead(400, HEIGHT - block_size - 42*10, 42, 42)
    rock_head.Idle()

    rock_head2 = RockHead(1300, HEIGHT-block_size -42*10, 42,42)
    rock_head2.Idle()

    rock_head2 = RockHead(3200, HEIGHT-block_size -42*10, 42,42)
    rock_head2.Idle()
    
    final = FinalZone(WIDTH*4 - 150, HEIGHT - block_size - 108, 46, 56)
    final.idle()

    # 아이템 리스트에 넣고 관리하기
    items = []
    health_item01 = HealthItem(block_size * 3, HEIGHT - block_size*4 -32- 16 , 32, 32)
    health_item01.idle()
    health_item02 = HealthItem(3000, HEIGHT - block_size*4 - 32- 16 , 32, 32)
    health_item02.idle()
    health_item03 = HealthItem(2000, HEIGHT - block_size*4 - 32- 16 , 32, 32)
    health_item03.idle()
    items.append(health_item01)
    items.append(health_item02)
    items.append(health_item03)

    obstacles = [] # for obstacle
    obstacles.append(saw)
    obstacles.append(saw2)
    obstacles.append(rock_head)
    obstacles.append(rock_head2)
    obstacles.append(final)

    floor = [Block(i*block_size, HEIGHT - block_size, block_size,1) for i in range(-WIDTH//block_size, WIDTH * 4 //block_size)]

    objects = [*floor, Block(-block_size, HEIGHT - block_size*3, block_size,1) ,
                       Block(0, HEIGHT - block_size*2, block_size,1), 
                       Block(block_size * 3, HEIGHT - block_size*4, block_size,1), 
                       Block(3000-96, HEIGHT - block_size*2, block_size,1),  # 바닥
                       Block(2000, HEIGHT - block_size*2, block_size,1),
                saw, saw2, rock_head, rock_head2, final, health_item01, health_item02, health_item03,
                enemys[0],enemys[1],enemys[2], enemys[3],enemys[4],enemys[5],enemys[6],enemys[7],enemys[8],enemys[9]] 

    return background, bg_image, objects,enemys, obstacles, sound

#=========================================make level 2====================================================
def make_level_2():
    sound = pygame.mixer.Sound("music/xDeviruchi - The Icy Cave .wav")
    background, bg_image = get_background("Gray.png")
    block_size = 96

    floor = [Block(i*block_size, HEIGHT - block_size, block_size,2) for i in range(-WIDTH//block_size, WIDTH * 2 //block_size)]
    boss = BOSS(400, HEIGHT - block_size - 250 - 64, 32, 32, 400 + 100, "fire")
    enemys = [boss]
    
    objects = [*floor, Block(block_size, HEIGHT - block_size*2, block_size,1),
                       Block(WIDTH, HEIGHT - block_size*2, block_size,1)]
    return background, bg_image, objects, enemys, sound

#=========================================draw====================================================
def draw(window, background, bg_image, player, objects, offset_x, bullets,elements, enemys, bossbullets, bossskills):
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
    for bullet in bossbullets:
        bullet.draw(window, offset_x)
    for skill in bossskills:
        skill.draw(window, offset_x)
        
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
    
    if game_level == 2:
        pygame.draw.rect(window,(255,0,0), (700, 10, enemys[-1].health*10, 25))
        pygame.draw.rect(window,(255,255,255), (700, 10, 20*10, 25), 4)

    player.draw(window, offset_x)
    pygame.display.update()

#================================================global function================================================
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


def handle_move(player, objects,game_level, game_over):
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
            obj.eat = True

        if obj and obj.name == "boss":
            print("boss hit!!")

        if obj and obj.name == "final":
            print("next level")
            game_level = 2
            game_over = 1
    
    return game_level, game_over

def game_scene(text="GAME OVER"):
    window.fill((80,80,80))
    font = pygame.font.SysFont("arialblack", 40)
    draw_text(text, font, "black", 350, 400, window)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()

    pygame.display.update()
#================================================main loop================================================
run = True
restart_button = Button(WIDTH // 2 - 50, HEIGHT // 2 + 100, restart_img)
start_button = Button(WIDTH // 2 - 350, HEIGHT // 2 + 50, start_img)
exit_button = Button(WIDTH // 2 + 150, HEIGHT // 2 + 50, exit_img)

offset_x = 0
scroll_area_width = 200

# for player
bullets = []
bullets = []
elements = [] # for increase skill gage / but now for ammo
bossbullets = [] # for boss attack
bossskills = []

player = Player(100,100,50,50)

sound = pygame.mixer.Sound("music/xDeviruchi - Minigame .wav")
sound.play(-1)
sound.set_volume(0.2)

attacksound = pygame.mixer.Sound("music/attack.wav")
attacksound.set_volume(5)
jumpsound = pygame.mixer.Sound("music/Jump.wav")
jumpsound.set_volume(2)
grasssound = pygame.mixer.Sound("music/Earth.wav")
grasssound.set_volume(2)
firesound = pygame.mixer.Sound("music/Fire.wav")
firesound.set_volume(2)
watersound = pygame.mixer.Sound("music/Water.wav")
watersound.set_volume(2)


while run:
    clock.tick(FPS)
    window.fill((121,70,99))
    font1 = pygame.font.SysFont("arialblack", 70)
    font2 = pygame.font.SysFont("arialblack", 20)
    font3 = pygame.font.SysFont("arialblack", 30)

    draw_text("Elemental Dungeon",font1,"black", 130, 100, window)
    draw_text("Control key", font3,"black", WIDTH//2 - 350, HEIGHT -150, window)
    draw_text("arrow key: move   s: jump", font2,"black", WIDTH//2 - 350, HEIGHT -100, window)
    draw_text("a: normal attack   q:grass attack   w: fire attack   e: water attack", font2,"black", WIDTH//2 - 350, HEIGHT-50, window)

    if main_menu == True:
        if exit_button.draw():
            run = False
        if start_button.draw():
            main_menu = False
    else:
        if game_over == -1:
            game_scene()
            if restart_button.draw():
                game_over = 1
                main_menu = False
                if game_level == 2: 
                    game_level = 1
                player = Player(100,100,50,50)
                offset_x = 0
                background, bg_image, objects, enemys, obstacles,sound = make_level_1()

        # game_clear
        if game_over == -2:
            game_scene("GAME CLEAR")

        # game_start
        if game_over == 1:
            if game_level == 1:
                background, bg_image, objects, enemys, obstacles,sound = make_level_1()
                game_over = 0

            if game_level == 2:
                background, bg_image, objects, enemys,sound = make_level_2()
                #player.reset(100,100,50,50)
                player.rect.x = 100
                player.rect.y = 100
                offset_x = 0
                game_over = 0

        if game_over == 0:
            game_over = player.loop(FPS, game_over)
            for e in enemys:
                e.loop(FPS)
            for o in obstacles:
                o.loop()

            game_level, game_over = handle_move(player, objects, game_level, game_over)             
            draw(window, background, bg_image, player, objects, offset_x, elements, bullets, enemys, bossbullets, bossskills)
            if game_level == 1:
                if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or ((player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
                    offset_x += player.x_vel 
        
            skillcnt = 0
            if enemys[-1].name == "boss":
                boss = enemys[-1]
                # 스킬 방향 체크
                if player.rect.centerx - boss.rect.centerx < 0:
                    facing = -1
                    boss.direction = "left"
                else:
                    facing = 1
                    boss.direction = "right"
                if boss.can_attack1:
                    skillcnt +=1
                    if skillcnt < FPS * 0.02:
                        bossbullet = Projectile(boss.rect.centerx, player.rect.centery, 10, (0,0,0), facing)
                        bossbullets.append(bossbullet)
                        skillcnt = 0

                if boss.can_attack2:
                    skillcnt +=1
                    if skillcnt < FPS * 0.02:
                        randx = randint(0, WIDTH)
                        bossskill = Projectile(randx, 0, 20, (255,255,255), 1)
                        bossskills.append(bossskill)
                        skillcnt = 0

            # 보스 투사체 발사
            for bb in bossbullets:
                if bb.x > boss.rect.centerx - 700 and bb.x < boss.rect.centerx + 700:
                    bb.x += bb.velocity
                    if bb.x == player.rect.centerx and (bb.y >= player.rect.centery-5 or bb.y <= player.rect.centery + 5):
                        bossbullets.pop(bossbullets.index(bb))
                        player.make_hit(5)
                else:
                    bossbullets.pop(bossbullets.index(bb))

            for ss in bossskills:
                if ss.y < HEIGHT:
                    ss.y += ss.velocity
                    if ss.x == player.rect.centerx and (ss.y >= player.rect.centery-5 or ss.y <= player.rect.centery + 5):
                        bossskills.pop(bossskills.index(ss))
                        player.make_hit(10)
                else:
                    bossskills.pop(bossskills.index(ss))

            # character attack to enemy
            for b in bullets:
                if b.x > player.rect.centerx - 700 and b.x < player.rect.centerx + 700:
                    b.x += b.velocity
                    for i in range(len(enemys)):
                        # 보스 피격처리
                        if enemys[i].name == "boss":
                            if (b.x >=enemys[i].rect.centerx-10 and b.x <= enemys[i].rect.centerx + 10):
                                if enemys[i].elemental == "fire" and b.color == "blue":
                                    enemys[i].health -= 1
                                    enemys[i].damaged = True
                                elif enemys[i].elemental == "water" and b.color == "green":
                                    enemys[i].health -= 1
                                    enemys[i].damaged = True
                                elif enemys[i].elemental == "grass" and b.color == "red":
                                    enemys[i].health -= 1
                                    enemys[i].damaged = True
                                else:
                                    print("not damage")
                                bullets.pop(bullets.index(b))
                                
                        elif (b.x >= enemys[i].rect.centerx-10 and b.x <= enemys[i].rect.centerx + 10) and (b.y >= enemys[i].rect.centery-10 and b.y <= enemys[i].rect.centery + 10):
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
                    if player.current_skill1_gage > 10:
                        player.current_skill1_gage = 10
                    if player.current_skill2_gage > 10:
                        player.current_skill2_gage = 10
                    if player.current_skill3_gage > 10:
                        player.current_skill3_gage = 10

            for e in enemys:
                if e.name == "boss":
                    if boss.health <= 0:
                        game_over = -2
                        #game_scene("GAME CLEAR")
                        #run = False
                elif e.health <= 0:
                    tempX = e.rect.centerx
                    #enemys.pop()
                    if tempX != 0:
                        if e.elemental == "grass":
                            element = Elements(tempX, HEIGHT - block_size - 30, 30, "green")
                        if e.elemental == "fire":
                            element = Elements(tempX, HEIGHT - block_size - 30, 30, "red")
                        if e.elemental == "water":
                            element = Elements(tempX, HEIGHT - block_size - 30, 30, "blue")
                        tempX = 0
                        elements.append(element)            
            
    #==========================================key board input==========================================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN:
            # jump
            if event.key == pygame.K_s and player.jump_count < 2:
                player.jump()
                jumpsound.play()
            # attack
            if event.key == pygame.K_a:
                player.attack()
                attacksound.play()
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
                grasssound.play()
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
                firesound.play()
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
                watersound.play()
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

    pygame.display.update()

pygame.quit()