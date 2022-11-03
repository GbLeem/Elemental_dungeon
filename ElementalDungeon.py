import cocos
from cocos.director import director
import pyglet
from pyglet.window import key


class Mover(cocos.actions.Move):
    def step(self, dt):
        super().step(dt)
        vel_x = (keyboard[key.RIGHT] - keyboard[key.LEFT]) * 500
        vel_y = (keyboard[key.UP] - keyboard[key.DOWN]) * 500
        self.target.velocity = (vel_x, vel_y)
        scroller.set_focus(self.target.x, self.target.y)


class PlayerLayer(cocos.layer.ScrollableLayer):
    def __init__(self):
        super().__init__()

        img = pyglet.image.load("img/Idle.png")
        img_grid = pyglet.image.ImageGrid(img, 1, 11, item_width=32, item_height=32)

        # for debug
        #print(img_grid[0:])

        anim = pyglet.image.Animation.from_image_sequence(img_grid[0:], 0.1, loop=True)
        
        sprite = cocos.sprite.Sprite(anim)
        sprite.position = 200, 500
        sprite.velocity = (0,0)
    
        sprite.do(Mover())

        self.add(sprite)


# chapter14 tilemap collider 추가 필요
class TileMap():
    def __init__(self):
        bg = cocos.tiles.load("img/tile/testmap.tmx")
        self.layer01 = bg["layer01"]


class BackGroundLayer(cocos.layer.ScrollableLayer):
    def __init__(self):
        super().__init__()

        bg = cocos.sprite.Sprite("img/background.png")
        
        bg.position = bg.width//2, bg.height//2

        self.px_width = bg.width
        self.px_height = bg.height

        self.add(bg)
    


# class Sprite02(cocos.sprite.Sprite):
#     def __init__(self):
#         #image, position, rotation, scale, opacity, color, anchor, **kwargs
#         super().__init__("img/Fall.png", scale= 2)
#         self.position = 640, 360


# class MainLayer(cocos.layer.Layer):
#     def __init__(self):
#         super().__init__()
#         label = cocos.text.Label("Elemental Dungeon", font_size = 32, anchor_x = "center", anchor_y = "center")
        
#         size = director.get_window_size()
#         print(size)
#         label.position = size[0]/2, size[1]/2
#         self.add(label)


if __name__ == '__main__':
    director.init(width = 640, height = 640, caption = "Elemental Dungeon")

    #key board input
    keyboard = key.KeyStateHandler()
    director.window.push_handlers(keyboard)

    # sprite layer
    spr01_layer = PlayerLayer()
    
    #background layer
    bg_layer = BackGroundLayer()
    scroller = cocos.layer.ScrollingManager()
    scroller.add(bg_layer)
    scroller.add(spr01_layer)

    #tilemap layer
    bg_tile = TileMap()
    scroller.add(bg_tile.layer01)

    # create Scene
    testScene = cocos.scene.Scene() #한번에 하나의 Scene만 가능
    
    testScene.add(scroller, 0, "background")
    #testScene.add(spr01_layer, 1, "player1") # layer의 층 설정 가능, layer의 이름 설정 가능
    cocos.director.director.run(testScene)