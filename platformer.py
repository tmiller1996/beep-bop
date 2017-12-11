#!/usr/bin/env python3
from os import path
import os
import sys
import random
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
PLAYER_START_Y = 420

PLATFORM_WIDTH = 210
PLATFORM_HEIGHT = 70

BASE_VX = 8
MOVE_VX = 6
JUMP_VY = 7

VOICE_CONSTANT = 5.2

PLAYER_OPEN_IMG = path.join('data', 'playerbrennusjumping.bmp')
PLAYER_IMG = path.join('data', 'playerbrennus.bmp')
BACKGROUND_IMG = path.join('data', 'background.bmp')
PLATFORM_IMG = path.join('data', 'platform.bmp')

GAMEOVER_TXT = path.join('data', 'gameover.txt')
NIRVANA_TXT = path.join('data', 'nirvana.txt')

FPS = 60


def restart():
    python = sys.executable
    os.execl(python, python, *sys.argv)


def gameover_msg():
    """Grab a random line from gameover.txt"""
    try:
        lines = tuple(open(GAMEOVER_TXT, 'r'))
        lines = map(lambda line: line[:-1], lines)
        return random.choice(list(lines))
    except FileNotFoundError as fnfe:
        print(str(fnfe))


def nirvana_msg():
    """Grab a random line from nirvana.txt"""
    try:
        lines = tuple(open(NIRVANA_TXT, 'r'))
        lines = map(lambda line: line[-1], lines)
        return random.choice(list(lines))
    except FileNotFoundError as fnfe:
        print(str(fnfe))


def gameover_surface():
    """Construct a surface for the Gameover display"""
    font = pygame.font.SysFont('monospace', 33, bold=True)
    gameover_label = font.render('Game over', 1, (255, 50, 255))
    flavor_label = font.render(gameover_msg(), 1, (255, 50, 255))
    keypress_label = font.render('Press any key to restart', 1, (255, 50, 255))
    surface = pygame.Surface([500, 300])
    surface.fill((50, 50, 255))
    surface.blit(gameover_label,
                          ((surface.get_width() - gameover_label.get_width()) / 2,
                           (surface.get_height() - gameover_label.get_height() - flavor_label.get_height() * 2) / 2))
    surface.blit(flavor_label,
                          ((surface.get_width() - flavor_label.get_width()) / 2,
                           (surface.get_height() - flavor_label.get_height()) / 2))
    surface.blit(keypress_label,
                          ((surface.get_width() - keypress_label.get_width()) / 2,
                           (surface.get_height() - keypress_label.get_height() + flavor_label.get_height() * 2) / 2))
    return surface


def nirvana_surface():
    """Construct a surface for the nirvana display"""
    font = pygame.font.SysFont('monospace', 33, bold=True)
    enlightenment_label = font.render('Enlightenment', 1, (255, 50, 255))
    flavor_label = font.render(nirvana_msg(), 1, (255, 50, 255))
    keypress_label = font.render('Press any key to restart', 1, (255, 50, 255))
    surface = pygame.Surface([500, 300])
    surface.fill((50, 50, 255))
    surface.blit(enlightenment_label,
                          ((surface.get_width() - enlightenment_label.get_width()) / 2,
                           (surface.get_height() - enlightenment_label.get_height() - flavor_label.get_height() * 2) / 2))
    surface.blit(flavor_label,
                          ((surface.get_width() - flavor_label.get_width()) / 2,
                           (surface.get_height() - flavor_label.get_height()) / 2))
    surface.blit(keypress_label,
                          ((surface.get_width() - keypress_label.get_width()) / 2,
                           (surface.get_height() - keypress_label.get_height() + flavor_label.get_height() * 2) / 2))
    return surface


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
    """A level, with platforms and an ending (ish)"""
    def __init__(self, player):
        self.platforms = sprite.Group()
        self.enemies = sprite.Group()
        self.player = player
        self.limit = -1000
        self.scroll = 0

    def update(self):
        self.platforms.update()
        self.enemies.update()

    def draw(self, screen):
        self.platforms.draw(screen)
        self.enemies.draw(screen)

    def scroll_world(self, scrollx):
        self.scroll += scrollx
        # TODO if we do scrolling background, apply that here
        for platform in self.platforms:
            platform.rect.x += scrollx
        for enemy in self.enemies:
            enemy.rect.x += scrollx

    def add_platform(self, x, y) -> None:
        platform = Platform()
        platform.rect.x = x
        platform.rect.y = y
        platform.player = self.player
        self.platforms.add(platform)


def build_level(level: Level) -> None:
    # TODO build level with random gaps and height variations
    # but for right now we'll just place two platforms and a gap, 10 times
    i = 0
    while i < 30:
        level.add_platform(i * PLATFORM_WIDTH, 500)
        level.add_platform((i + 1) * PLATFORM_WIDTH, 500)
        i += 3
    level.limit = -5000


def main() -> None:
    pygame.init()

    random.seed()

    size = [SCREEN_WIDTH, SCREEN_HEIGHT]
    screen = display.set_mode(size)

    display.set_caption(TITLE)

    background = image.load(BACKGROUND_IMG)

    player = Player()

    level = Level(player)
    player.level = level
    build_level(level)

    sprites = sprite.Group()

    player.rect.x = PLAYER_START_X
    player.rect.y = PLAYER_START_Y
    sprites.add(player)

    clock = pygame.time.Clock()

    last_volume = float(sys.float_info.max)

    def mic_callback(volume, pitch):
        nonlocal last_volume
        if volume > last_volume * VOICE_CONSTANT:
            player.scream()
        last_volume = volume

    mic = microphone.Microphone()
    mic.add_callback(mic_callback)
    mic.start()

    done = False
    gameover = None
    nirvana = None

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYUP:
                if gameover is not None or nirvana is not None:
                    restart() # lol

        sprites.update()

        level.update()

        # scroll right
        if player.rect.right >= SCROLL_RIGHT:
            diff = player.rect.right - SCROLL_RIGHT
            player.rect.right = SCROLL_RIGHT
            level.scroll_world(-diff)

        # scroll left
        if player.rect.left <= SCROLL_LEFT:
            diff = SCROLL_LEFT - player.rect.left
            player.rect.left = SCROLL_LEFT
            level.scroll_world(diff)

        if player.rect.y + player.rect.height == SCREEN_HEIGHT:
            if gameover is None and nirvana is None:
                gameover = gameover_surface()

        position = player.rect.x + level.scroll
        if position < level.limit:
            player.rect.x = SCROLL_LEFT
            if nirvana is None and gameover is None:
                nirvana = nirvana_surface()

        # render
        screen.blit(background, (0, 0))
        level.draw(screen)
        sprites.draw(screen)
        if nirvana is not None:
            screen.blit(nirvana, ((screen.get_width() - nirvana.get_width()) / 2,
                                  (screen.get_height() - nirvana.get_height()) / 2))
        if gameover is not None:
            screen.blit(gameover,
                        ((screen.get_width() - gameover.get_width()) / 2,
                         (screen.get_height()- gameover.get_height()) / 2))

        # limit FPS
        clock.tick(FPS)

        # flip-a-roo
        display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
