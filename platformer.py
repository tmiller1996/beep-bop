from os import path

try:
    import pygame as pg
except:
    print("Failed to import pygame")

TITLE = 'The man who would never be what they wanted him to be'

# color constants
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 50, 255)
PURPLE = (255, 50, 255)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCROLL_RIGHT = 500
SCROLL_LEFT = 120

PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60
PLAYER_START_X = 340
PLAYER_START_Y = SCREEN_HEIGHT - PLAYER_HEIGHT

BASE_VX = 0

PLAYER_OPEN_IMG = path.join('data', 'player_open.bmp')
PLAYER_IMG = path.join('data', 'player.bmp')

FPS = 60


class Player(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.player_img = pg.image.load(PLAYER_IMG)
        self.player_open_img = pg.image.load(PLAYER_OPEN_IMG)

        self.image = self.player_img

        self.rect = self.image.get_rect()

        self.vx = BASE_VX
        self.vy = 0

        self.level = None

    def update(self):
        self.gravity()

        self.rect.x += self.vx

        # horizontal collision
        hits = pg.sprite.spritecollide(self, self.level.platforms, False)
        for hit in hits:
            if self.vx > 0:
                self.rect.right = hit.rect.left
            elif self.vx < 0:
                self.rect.left = hit.rect.right

        self.rect.y += self.vy

        # vertical collision
        hits = pg.sprite.spritecollide(self, self.level.platforms, False)
        for hit in hits:
            if self.vy > 0:
                self.rect.bottom = hit.rect.top
            elif self.vy < 0:
                self.rect.top = hit.rect.bottom

            self.vy = 0

            # the original image is restored when the player lands on a platform
            self.image = self.player_img

    def gravity(self):
        if self.vy == 0:
            self.vy = 1
        else:
            self.vy += .35

        if self.rect.y >= SCREEN_HEIGHT - self.rect.height and self.vy >= 0:
            self.vy = 0
            self.rect.y = SCREEN_HEIGHT - self.rect.height

    def jump(self):
        # check if there is a platform beneath us
        self.rect.y += 2
        hits = pg.sprite.spritecollide(self, self.level.platforms, False)
        self.rect.y -= 2

        if len(hits) > 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.vy = -10

    def left(self):
        self.vx = BASE_VX - 6

    def right(self):
        self.vx = BASE_VX + 6

    def stop(self):
        self.vx = BASE_VX

    def scream(self):
        self.image = self.player_open_img
        self.jump()


# TODO give Platform a constant width, height, and sprite
class Platform(pg.sprite.Sprite):
    def __init__(self, width, height):
        super().__init__()

        self.image = pg.Surface([width, height])
        self.image.fill(RED)

        self.rect = self.image.get_rect()


class Level(object):
    def __init__(self, player):
        self.platforms = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.player = player

        self.limit = None
        self.background = None
        self.scroll = 0

    def update(self):
        self.platforms.update()
        self.enemies.update()

    def draw(self, screen):
        # draw background image
        # TODO draw a nice background
        screen.fill(BLUE)

        self.platforms.draw(screen)
        self.enemies.draw(screen)

    def scroll_world(self, scrollx):
        self.scroll += scrollx
        for platform in self.platforms:
            platform.rect.x += scrollx
        for enemy in self.enemies:
            enemy.rect.x += scrollx


class Level01(Level):
    def __init__(self, player):
        Level.__init__(self, player)

        self.limit = -1000

        level = [[210, 70, 500, 500],
                 [210, 70, 200, 400],
                 [210, 70, 600, 300],
                 ]

        for arr in level:
            platform = Platform(arr[0], arr[1])
            platform.rect.x = arr[2]
            platform.rect.y = arr[3]
            platform.player = self.player
            self.platforms.add(platform)


class Level_02(Level):
    def __init__(self, player):
        Level.__init__(self, player)

        self.limit = -1000

        level = [[210, 30, 450, 570],
                 [210, 30, 850, 420],
                 [210, 30, 1000, 520],
                 [210, 30, 1120, 280]]

        # TODO move this to Level class
        for arr in level:
            platform = Platform(arr[0], arr[1])
            platform.rect.x = arr[2]
            platform.rect.y = arr[3]
            platform.player = self.player
            self.platforms.add(platform)


def main():
    pg.init()

    size = [SCREEN_WIDTH, SCREEN_HEIGHT]
    screen = pg.display.set_mode(size)

    pg.display.set_caption(TITLE)

    player = Player()

    levels = [Level01(player),]

    current_level = 0
    player.level = levels[current_level]

    sprites = pg.sprite.Group()

    player.rect.x = PLAYER_START_X
    player.rect.y = PLAYER_START_Y
    sprites.add(player)

    done = False

    clock = pg.time.Clock()

    while not done:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True

            # TODO temp code, this should be replaced by the mic
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_LEFT:
                    player.left()
                if event.key == pg.K_RIGHT:
                    player.right()
                if event.key == pg.K_UP:
                    player.jump()
                if event.key == pg.K_s:
                    player.scream()

            if event.type == pg.KEYUP:
                if event.key == pg.K_LEFT and player.vx < 0:
                    player.stop()
                if event.key == pg.K_RIGHT and player.vx > 0:
                    player.stop()

        sprites.update()

        levels[current_level].update()

        # scroll right
        if player.rect.right >= SCROLL_RIGHT:
            diff = player.rect.right - SCROLL_RIGHT
            player.rect.right = SCROLL_RIGHT
            levels[current_level].scroll_world(-diff)

        # scroll left
        if player.rect.left <= SCROLL_LEFT:
            diff = SCROLL_LEFT - player.rect.left
            player.rect.left = SCROLL_LEFT
            levels[current_level].scroll_world(diff)

        # go to next level if end of level is reached
        position = player.rect.x + levels[current_level].scroll
        if position < levels[current_level].limit:
            player.rect.x = SCROLL_LEFT
            if current_level < len(levels) - 1:
                current_level += 1
                player.level = levels[current_level]

        # render
        levels[current_level].draw(screen)
        sprites.draw(screen)

        # limit FPS
        clock.tick(FPS)

        # flip-a-roo
        pg.display.flip()

    pg.quit()

if __name__ == "__main__":
    main()