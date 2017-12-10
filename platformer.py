#!/usr/bin/env python3
from os import path
import sys
import microphone
import pygame
from pygame import image
from pygame import sprite
from pygame import display

TITLE = 'Beep Bop'

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCROLL_RIGHT = 500
SCROLL_LEFT = 120

PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60
PLAYER_START_X = 0
PLAYER_START_Y = 500 - PLAYER_HEIGHT

BASE_VX = 8
MOVE_VX = 6
JUMP_VY = 6

VOICE_CONSTANT = 6

PLAYER_OPEN_IMG = path.join('data', 'player_open.bmp')
PLAYER_IMG = path.join('data', 'player.bmp')
BACKGROUND_IMG = path.join('data', 'background.bmp')
PLATFORM_IMG = path.join('data', 'platform.bmp')

FPS = 60


class Player(sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.player_img = image.load(PLAYER_IMG)
        self.player_open_img = image.load(PLAYER_OPEN_IMG)

        self.image = self.player_img

        self.rect = self.image.get_rect()

        self.vx = BASE_VX
        self.vy = 0

        self.level = None

    def update(self):
        self.gravity()

        self.rect.x += self.vx

        # horizontal collision
        hits = sprite.spritecollide(self, self.level.platforms, False)
        for hit in hits:
            if self.vx > 0:
                self.rect.right = hit.rect.left
            elif self.vx < 0:
                self.rect.left = hit.rect.right

        self.rect.y += self.vy

        # vertical collision
        hits = sprite.spritecollide(self, self.level.platforms, False)
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
        hits = sprite.spritecollide(self, self.level.platforms, False)
        self.rect.y -= 2

        if len(hits) > 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.vy = -JUMP_VY

    def left(self):
        self.vx = BASE_VX - MOVE_VX

    def right(self):
        self.vx = BASE_VX + MOVE_VX

    def stop(self):
        self.vx = BASE_VX

    def scream(self):
        self.image = self.player_open_img
        self.jump()


class Platform(sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.image = image.load(PLATFORM_IMG)
        self.rect = self.image.get_rect()


class Level(object):
    def __init__(self, player):
        self.platforms = sprite.Group()
        self.enemies = sprite.Group()
        self.player = player

        self.limit = None

        self.background_sprites = sprite.Group()

        # TODO change this
        background = sprite.Sprite()
        background.image = image.load(BACKGROUND_IMG)
        background.rect = background.image.get_rect()
        self.background_sprites.add(background)

        self.scroll = 0

    def update(self):
        self.platforms.update()
        self.enemies.update()

    def draw(self, screen):
        self.background_sprites.draw(screen)
        self.platforms.draw(screen)
        self.enemies.draw(screen)

    def scroll_world(self, scrollx):
        self.scroll += scrollx
        # TODO if we do scrolling background, apply that here
        for platform in self.platforms:
            platform.rect.x += scrollx
        for enemy in self.enemies:
            enemy.rect.x += scrollx


def build_level(level):
    pass # TODO build level with random gaps and height variations


class Level01(Level):
    def __init__(self, player):
        Level.__init__(self, player)

        self.limit = -1000

        level = [[0, 500],
                 [210, 500],
                 [500, 500]]

        for arr in level:
            platform = Platform()
            platform.rect.x = arr[0]
            platform.rect.y = arr[1]
            platform.player = self.player
            self.platforms.add(platform)


def main():
    pygame.init()

    # TODO read gameover.txt to string array (line by line)

    size = [SCREEN_WIDTH, SCREEN_HEIGHT]
    screen = display.set_mode(size)

    display.set_caption(TITLE)

    player = Player()

    levels = [Level01(player)]

    current_level = 0
    player.level = levels[current_level]

    sprites = sprite.Group()

    player.rect.x = PLAYER_START_X
    player.rect.y = PLAYER_START_Y
    sprites.add(player)

    done = False

    clock = pygame.time.Clock()

    last_data = float(sys.float_info.max)

    def callback(data):
        nonlocal last_data
        if isinstance(data, str):
            print(data)
        else:
            if data > last_data * VOICE_CONSTANT:
                player.scream()
            last_data = data

    mic = microphone.Microphone(callback)
    mic.start()

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            # if event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_LEFT:
            #         player.left()
            #     if event.key == pygame.K_RIGHT:
            #         player.right()
            #     if event.key == pygame.K_UP:
            #         player.jump()
            #
            # if event.type == pygame.KEYUP:
            #     if event.key == pygame.K_LEFT and player.vx < 0:
            #         player.stop()
            #     if event.key == pygame.K_RIGHT and player.vx > 0:
            #         player.stop()

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

        # TODO if player hits ground, game over
        # add a restart button in the middle, with the text

        # go to next level if end of level is reached
        # TODO get rid of this, if the end is reached then the player reached nirvana
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
        display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
