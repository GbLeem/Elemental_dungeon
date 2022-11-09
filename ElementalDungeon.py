import cocos
from cocos.director import director
import pyglet
from pyglet.window import key
from cocos import mapcolliders


# 더 세분화 해야 할듯
class Mover(cocos.actions.Move):
    def step(self, dt):
        vel_x = (keyboard[key.RIGHT] - keyboard[key.LEFT]) * 200
        vel_y = (keyboard[key.UP] - keyboard[key.DOWN]) * 200
        dx = vel_x * dt
        dy = vel_y * dt
        
        # TODO: jump
        vel_z = keyboard[key.S]*100
        dz = vel_z*dt

        last = self.target.get_rect()
        new = last.copy()
        
        new.x += dx
        new.y += dy
        self.target.velocity = self.target.collide_map(last, new, vel_x, vel_y)

        self.target.position = new.center
        
        scroller.set_focus(*new.center)

        
      
        # keyboard input test
        normalattack = keyboard[key.A]
        firemode = keyboard[key.Q]
        grassmode = keyboard[key.W]
        airmode = keyboard[key.E]

        if normalattack != 0:
            self.attack()
        if firemode !=0:
            self.firemode()
        if grassmode !=0:
            self.grassmode()
        if airmode !=0:
            self.airmode()

    # def update(self):
    #     pressed = Mover.KEYS_PRESSED
    #     s_pressed = pressed[key.S] == 1
    #     if s_pressed:
    #         self.jump()

    def jump(self):
        print("jump")
        # keyinput = self.pressed[key.S]
        # if keyinput != 0:
        #     vel_z = keyinput * 100

        # self.target.velocity = vel_z
        # if vel_z != 0:

    def attack(self):
        print("attack")

    def firemode(self):
        print("fire mode")

    def grassmode(self):
        print("grass mode")
    
    def airmode(self):
        print("air mode")

class PlayerLayer(cocos.layer.ScrollableLayer):
    def __init__(self, collision_handler):
        super().__init__()

        img = pyglet.image.load("img/Idle.png")
        img_grid = pyglet.image.ImageGrid(img, 1, 11, item_width=32, item_height=32)

        # for debug
        #print(img_grid[0:])

        anim = pyglet.image.Animation.from_image_sequence(img_grid[0:], 0.1, loop=True)
        
        sprite = cocos.sprite.Sprite(anim)
        sprite.position = 50, 80
        sprite.velocity = (0,0)

        sprite.collide_map = collision_handler
    
        sprite.do(Mover())

        self.add(sprite)


class TileMap():
    def __init__(self):
        bg = cocos.tiles.load("img/tile/testmap01.tmx")
        self.layer01 = bg["layer01"]
        self.collision = bg["colliders"]


class BackGroundLayer(cocos.layer.ScrollableLayer):
    def __init__(self):
        super().__init__()

        bg = cocos.sprite.Sprite("img/background.png")
        
        bg.position = bg.width//2, bg.height//2

        self.px_width = bg.width
        self.px_height = bg.height

        self.add(bg)
    
# class GameSetting():
#     def __init__(self):
#         director.init(width = 640, height = 640, caption = "Elemental Dungeon")
#         #director.window.pop_handlers()

#         #key board input
#         keyboard = key.KeyStateHandler()
#         director.window.push_handlers(keyboard)

#         # sprite layer
#         bg_layer = BackGroundLayer()
#         scroller = cocos.layer.ScrollingManager()
#         scroller.add(bg_layer)

#         #tilemap layer
#         bg_tile = TileMap()
#         scroller.add(bg_tile.layer01)
#         scroller.add(bg_tile.collision)

#         mapcollider = mapcolliders.TmxObjectMapCollider()
#         mapcollider.on_bump_handler = mapcollider.on_bump_bounce
#         collision_handler = mapcolliders.make_collision_handler(mapcollider, bg_tile.collision)

#         #background layer
#         spr01_layer = PlayerLayer(collision_handler)
#         scroller.add(spr01_layer)

#     def make_scene(self):
#         testScene = cocos.scene.Scene() #한번에 하나의 Scene만 가능
#         testScene.add(scroller, 0, "background")
#         return testScene

if __name__ == '__main__':
    director.init(width = 640, height = 640, caption = "Elemental Dungeon")
    #director.window.pop_handlers()

    #key board input
    keyboard = key.KeyStateHandler()
    director.window.push_handlers(keyboard)

    # sprite layer
    bg_layer = BackGroundLayer()
    scroller = cocos.layer.ScrollingManager()
    scroller.add(bg_layer)

    #tilemap layer
    bg_tile = TileMap()
    scroller.add(bg_tile.layer01)
    scroller.add(bg_tile.collision)
    
    mapcollider = mapcolliders.TmxObjectMapCollider()
    mapcollider.on_bump_handler = mapcollider.on_bump_bounce
    collision_handler = mapcolliders.make_collision_handler(mapcollider, bg_tile.collision)

    #background layer
    spr01_layer = PlayerLayer(collision_handler)
    scroller.add(spr01_layer)

    # create Scene
    testScene = cocos.scene.Scene() #한번에 하나의 Scene만 가능
    #testScene.add(spr01_layer, 1, "player1") # layer의 층 설정 가능, layer의 이름 설정 가능
    testScene.add(scroller, 0, "background")
    cocos.director.director.run(testScene)
    #GameSetting()
    #testScene = GameSetting().make_scene