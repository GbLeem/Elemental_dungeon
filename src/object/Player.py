
import pygame

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