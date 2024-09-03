import pygame as pg
from random import randint, uniform
vec = pg.math.Vector2

# Configurações da tela e cores
WIDTH = 800
HEIGHT = 640
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
DARKGRAY = (40, 40, 40)
LIGHTGRAY = (140, 140, 140)

# Propriedades do Mob
MOB_SIZE = 16
MAX_SPEED = 4
MAX_FORCE = 0.15
WALL_LIMIT = 20
LOOK_AHEAD = 20
APPROACH_RADIUS = 120

class Wall(pg.sprite.Sprite):
    def __init__(self, x=0, y=0, s=32):
        self.groups = all_sprites, walls
        pg.sprite.Sprite.__init__(self, self.groups)
        if x == 0 and y == 0:
            x = randint(0, (WIDTH / s) - 1)
            y = randint(0, (HEIGHT / s) - 1)
        self.image = pg.Surface((s, s))
        self.image.fill(LIGHTGRAY)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x * s, y * s)
        self.radius = (self.rect.width * 1.414 / 2) + WALL_LIMIT

    def draw_vectors(self):
        pg.draw.circle(screen, CYAN, self.rect.center, int(self.radius), 2)


class Mob(pg.sprite.Sprite):
    def __init__(self):
        self.groups = all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = pg.Surface((MOB_SIZE, MOB_SIZE))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.pos = vec(randint(0, WIDTH), randint(0, HEIGHT))
        self.vel = vec(MAX_SPEED, 0).rotate(uniform(0, 360))
        self.acc = vec(0, 0)
        self.rect.center = self.pos

    def seek_with_approach(self, target):
        self.desired = (target - self.pos)
        dist = self.desired.length()
        self.desired.normalize_ip()
        if dist < APPROACH_RADIUS:
            self.desired *= dist / APPROACH_RADIUS * MAX_SPEED
        else:
            self.desired *= MAX_SPEED
        steer = (self.desired - self.vel)
        if steer.length() > MAX_FORCE:
            steer.scale_to_length(MAX_FORCE)
        return steer

    def avoid_obstacles(self, group):
        dyn_length = LOOK_AHEAD * self.vel.length() / MAX_SPEED
        ahead = self.pos + self.vel.normalize() * dyn_length
        ahead2 = self.pos + self.vel.normalize() * dyn_length / 2
        self.a = vec(ahead)
        self.a2 = vec(ahead2)
        most_threatening = self.find_most_threatening(group, ahead, ahead2)
        if most_threatening:
            steer = ahead - most_threatening.rect.center
            steer.normalize_ip()
            steer.scale_to_length(MAX_FORCE)
        else:
            steer = vec(0, 0)
        return steer

    def find_collision(self, obs, ahead, ahead2):
        obs_center = vec(obs.rect.center)
        d1 = obs_center.distance_to(ahead)
        d2 = obs_center.distance_to(ahead2)
        return (d1 <= obs.radius) or (d2 <= obs.radius)

    def find_most_threatening(self, group, ahead, ahead2):
        most_threatening = None
        for obs in group:
            collide = self.find_collision(obs, ahead, ahead2)
            if collide and (not most_threatening or self.pos.distance_to(obs.rect.center) < self.pos.distance_to(most_threatening.rect.center)):
                most_threatening = obs
        return most_threatening

    def update(self):
        mouse_pos = pg.mouse.get_pos()
        self.acc = self.seek_with_approach(mouse_pos) + self.avoid_obstacles(walls) * 2
        self.vel += self.acc
        if self.vel.length() > MAX_SPEED:
            self.vel.scale_to_length(MAX_SPEED)
        self.pos += self.vel
        if self.pos.x > WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH
        if self.pos.y > HEIGHT:
            self.pos.y = 0
        if self.pos.y < 0:
            self.pos.y = HEIGHT
        self.rect.center = self.pos

    def draw_vectors(self):
        scale = 25
        pg.draw.line(screen, GREEN, self.pos, (self.pos + self.vel * scale), 5)
        pg.draw.line(screen, RED, self.pos, (self.pos + self.acc * scale * 5), 5)
        ax = int(self.a.x)
        ay = int(self.a.y)
        ax2 = int(self.a2.x)
        ay2 = int(self.a2.y)
        pg.draw.circle(screen, CYAN, (ax, ay), 5)
        pg.draw.circle(screen, CYAN, (ax2, ay2), 5)

# Inicialização do Pygame
pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
clock = pg.time.Clock()

all_sprites = pg.sprite.Group()
walls = pg.sprite.Group()
Mob()

# Criação de paredes
for i in range(8):
    Wall()

paused = False
show_vectors = False
running = True
while running:
    clock.tick(FPS)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                running = False
            if event.key == pg.K_SPACE:
                paused = not paused
            if event.key == pg.K_v:
                show_vectors = not show_vectors
            if event.key == pg.K_m:
                Mob()
        if event.type == pg.MOUSEBUTTONDOWN:
            mpos = pg.mouse.get_pos()
            x = mpos[0] // 32
            y = mpos[1] // 32
            if event.button == 1:
                Wall(x=x, y=y, s=32)
            if event.button == 3:
                for sprite in all_sprites:
                    if sprite.rect.collidepoint(mpos):
                        sprite.kill()

    if not paused:
        all_sprites.update()
    pg.display.set_caption("{:.2f}".format(clock.get_fps()))
    screen.fill(DARKGRAY)
    all_sprites.draw(screen)
    if show_vectors:
        for sprite in all_sprites:
            sprite.draw_vectors()
    pg.display.flip()

pg.quit()
