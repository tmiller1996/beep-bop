import pygame as pg

from os import path


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 50, 255)
PURPLE = (255, 50, 255)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60

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
        self.rect.y += 2
        hits = pg.sprite.spritecollide(self, self.level.platforms, False)
        self.rect.y -= 2

        if len(hits) > 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.vy = -10

    def go_left(self):
        self.vx = BASE_VX - 6

    def go_right(self):
        self.vx = BASE_VX + 6

    def stop(self):
        self.vx = BASE_VX

    def scream(self):
        self.image = self.player_open_img
        self.jump()


class Platform(pg.sprite.Sprite):
    def __init__(self, width, height, color):
        super().__init__()

        self.image = pg.Surface([width, height])
        self.image.fill(color)

        self.rect = self.image.get_rect()


class Level(object):
    def __init__(self, player):
        self.platforms = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.player = player

        self.background = None

    def update(self):
        self.platforms.update()
        self.enemies.update()

    def draw(self, screen):
        # draw background image
        screen.fill(BLUE)

        self.platforms.draw(screen)
        self.enemies.draw(screen)


class Level01(Level):
    pass


def main():
    pg.init()

    size = [SCREEN_WIDTH, SCREEN_HEIGHT]
    screen = pg.display.set_mode(size)

    pg.display.set_caption('Platformer')

    player = Player()

    levels = [Level01(player)]

    current_level_index = 0
    current_level = levels[current_level_index]

    sprites = pg.sprite.Group()
    player.level = current_level

    player.rect.x = 340
    player.rect.y = SCREEN_HEIGHT - player.rect.height
    sprites.add(player)

    done = False

    clock = pg.time.Clock()

    while not done:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_LEFT:
                    player.go_left()
                if event.key == pg.K_RIGHT:
                    player.go_right()
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

        current_level.update()

        if player.rect.right > SCREEN_WIDTH:
            player.rect.right = SCREEN_WIDTH

        if player.rect.left < 0:
            player.rect.left = 0

        current_level.draw(screen)
        sprites.draw(screen)

        clock.tick(FPS)

        pg.display.flip()

    pg.quit()

if __name__ == "__main__":
    main()