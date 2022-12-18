import pygame
import sys
from os import listdir
from os.path import isfile, join

from object.Player import Player


# start
pygame.init()

clock = pygame.time.Clock()

pygame.display.set_caption("Platformer")

BG_COLOR = (255,255,255)
WIDTH, HEIGHT = 1000, 800
FPS = 60
PLAYER_VEL = 5

window = pygame.display.set_mode((WIDTH,HEIGHT))


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

def level(level):
    if level == 1:
        print("level 1")
    
    if level == 2:
        print("boss stage")

def main(window):
    # background, bg_image = get_background("Yellow.png")

    # block_size = 96

    player = Player(100,100,50,50)

    # enemy1 = Enemy(400, HEIGHT - block_size- 64, 32, 32, 700, "grass")
    # enemy2 = FireEnemy(1000, HEIGHT - block_size - 36-18, 32,30, 1000+400, "fire")
    # enemy3 = WaterBird(200, HEIGHT - block_size*4-32, 32, 32, 400+100,"water")
    # enemy4 = FireBunny(96, HEIGHT - block_size - 34*2-17, 32, 32, 196,"fire")

    # boss = BOSS(1400, HEIGHT - block_size - 250 - 32, 32, 32, 1400 + 500, "fire")

    # enemys = [enemy1,enemy2,enemy3,enemy4,boss]


    # # enemys.append(enemy1)
    # # enemys.append(enemy2)

    # saw = Saw(96*10, HEIGHT - block_size - 76, 38, 76)
    # saw.on()

    # rock_head = RockHead(400, HEIGHT - block_size - 42*10, 42, 42)
    # rock_head.Idle()

    # # 아이템 리스트에 넣고 관리하기
    # items = []
    # health_item01 = HealthItem(block_size * 3, HEIGHT - block_size*4 -32- 16 , 32, 32)
    # health_item01.idle()
    # items.append(health_item01)

    # #blocks = [Block(0, HEIGHT-block_size, block_size)]
    # floor = [Block(i*block_size, HEIGHT - block_size, block_size) for i in range(-WIDTH//block_size, WIDTH * 2 //block_size)]

    # objects = [*floor, Block(-block_size, HEIGHT - block_size*3, block_size) ,Block(0, HEIGHT - block_size*2, block_size), Block(block_size * 3, HEIGHT - block_size*4, block_size), 
    #             saw, rock_head, health_item01, enemys[0],enemys[1],enemys[2], enemys[3]] 

    # offset_x = 0
    scroll_area_width = 200

    # bullets = []
    # elements = [] # for increase skill gage / but now for ammo

    # element_draw_count = 0

    run = True

    while(run):
        clock.tick(FPS)
        
    #     for b in bullets:
    #         if b.x > player.rect.centerx - 700 and b.x < player.rect.centerx + 700:
    #             b.x += b.velocity
    #             for i in range(len(enemys)):
    #                 if (b.x >= enemys[i].rect.centerx-10 and b.x <= enemys[i].rect.centerx + 10) and (b.y >= enemys[i].rect.centery-10 and b.y <= enemys[i].rect.centery + 10):
    #                     if bullet.color == "red":
    #                         if enemys[i].elemental == "grass":
    #                             enemys[i].health -= 4
    #                         elif enemys[i].elemental == "water":
    #                             enemys[i].health -= 1
    #                     elif bullet.color == "green":
    #                         if enemys[i].elemental == "water":
    #                             enemys[i].health -= 4
    #                         elif enemys[i].elemental == "fire":
    #                             enemys[i].health -= 1
    #                     elif bullet.color == "blue":
    #                         if enemys[i].elemental == "fire":
    #                             enemys[i].health -= 4
    #                         elif enemys[i].elemental == "grass":
    #                             enemys[i].health -= 1
    #                     else:
    #                         enemys[i].health -= 2 # bullet 이랑 skill damage를 적용해야 함!! 지금은 그냥 임시 숫자임
                        
    #                     enemys[i].damaged = True
    #                     bullets.pop(bullets.index(b))
    #                 else:
    #                     enemys[i].damaged = False
    #         else:
    #             bullets.pop(bullets.index(b))


    #     # getting item
    #     for e in elements:
    #         if (player.rect.centerx >= e.x-5 and player.rect.centerx <= e.x+5) and (player.rect.centery >= e.y-5 and player.rect.centery <= e.y+5):
    #         #if player.rect.centerx == e.x:
    #             if e.color == "green":
    #                 player.current_skill1_gage += 5
    #             elif e.color == "red":
    #                 player.current_skill2_gage += 5
    #             elif e.color == "blue":
    #                 player.current_skill3_gage += 5

    #             player.current_attack_gage += 5
    #             elements.pop(elements.index(e))

    #             # gage 넘어가지 않게 처리
    #             if player.current_attack_gage > 20:
    #                 player.current_attack_gage = 20


    #     # item spawn => 한번씩만 만들어야함!
    #     for i in range(len(enemys)):
    #         if enemys[i].health <= 0:
    #             if element_draw_count == 0:
    #                 if enemys[i].elemental == "grass":
    #                     element = Elements(enemys[i].rect.centerx, HEIGHT - block_size - 30, 30, "green")
    #                 if enemys[i].elemental == "fire":
    #                     element = Elements(enemys[i].rect.centerx, HEIGHT - block_size - 30, 30, "red")
    #                 if enemys[i].elemental == "water":
    #                     element = Elements(enemys[i].rect.centerx, HEIGHT - block_size - 30, 30, "blue")

    #                 elements.append(element)


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break

            # if event.type == pygame.KEYDOWN:
            #     # jump
            #     if event.key == pygame.K_s and player.jump_count < 2:
            #         player.jump()

            #     # attack
            #     if event.key == pygame.K_a:
            #         player.attack()
                
            #         if player.direction == "left":
            #             facing = -1
            #         else:
            #             facing = 1

            #         if player.current_attack_gage > 0:
            #             bullet = Projectile(player.rect.centerx, player.rect.centery, 6, (0,0,0), facing)                    
            #             bullets.append(bullet)
            #             player.current_attack_gage -= 1
            #         if player.current_attack_gage == 0:
            #             player.can_attack = False
                
            #     # skill1 grass
            #     if event.key == pygame.K_q:
            #         player.attack()
            #         if player.direction == "left":
            #             facing = -1
            #         else:
            #             facing = 1

            #         if player.current_skill1_gage > 0:
            #             bullet = Projectile(player.rect.centerx, player.rect.centery, 6, "green", facing)                    
            #             bullets.append(bullet)
            #             player.current_skill1_gage -= 1
            #         if player.current_skill1_gage == 0:
            #             player.can_attack = False

            #     # skill2 fire
            #     if event.key == pygame.K_w:
            #         player.attack()
            #         if player.direction == "left":
            #             facing = -1
            #         else:
            #             facing = 1
            #         if player.current_skill2_gage > 0:
            #             bullet = Projectile(player.rect.centerx, player.rect.centery, 6, "red", facing)                    
            #             bullets.append(bullet)
            #             player.current_skill2_gage -= 1
            #         if player.current_skill2_gage == 0:
            #             player.can_attack = False
                
            #     # skill3 water
            #     if event.key == pygame.K_e:
            #         player.attack()
            #         if player.direction == "left":
            #             facing = -1
            #         else:
            #             facing = 1
            #         if player.current_skill3_gage > 0:
            #             bullet = Projectile(player.rect.centerx, player.rect.centery, 6, "blue", facing)                    
            #             bullets.append(bullet)
            #             player.current_skill3_gage -= 1
            #         if player.current_skill3_gage == 0:
            #             player.can_attack = False
        
        player.loop(FPS)
        # enemys[0].loop(FPS)
        # enemys[1].loop(FPS)
        # enemys[2].loop(FPS)
        # enemys[3].loop(FPS)
        # enemys[4].loop(FPS)

        # saw.loop()
        # rock_head.loop(FPS)
        # health_item01.loop()
        # handle_move(player, objects)
        
        # draw(window, background, bg_image, player,objects, offset_x,elements, bullets, enemys)

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or ((player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel

    pygame.quit()
    quit()

if __name__ == "__main__":
    main(window)
