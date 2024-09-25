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
MAX_FORCE = 0.3
WALL_LIMIT = 20
LOOK_AHEAD = 40
APPROACH_RADIUS = 120

class Wall(pg.sprite.Sprite):
    def __init__(self, x, y, s=32):
        self.groups = all_sprites, walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = pg.Surface((s, s))
        self.image.fill(LIGHTGRAY)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x * s, y * s)
        self.radius = (self.rect.width * 1.414 / 2) + WALL_LIMIT

    def draw_vectors(self):
        pg.draw.circle(screen, CYAN, self.rect.center, int(self.radius), 2)

class Mob(pg.sprite.Sprite):
    def __init__(self):
        self.groups = all_sprites, mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = pg.Surface((MOB_SIZE, MOB_SIZE))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.pos = vec(randint(0, WIDTH // 2 - 50), randint(0, HEIGHT))
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
        steer = vec(0, 0)
        for wall in group:
            dist = self.pos.distance_to(wall.rect.center)
            if dist < wall.radius + self.rect.width / 2:
                diff = self.pos - wall.rect.center
                steer += diff.normalize() * (wall.radius + self.rect.width / 2 - dist)
        if steer.length() > MAX_FORCE:
            steer.scale_to_length(MAX_FORCE)
        return steer * 2  # Aumentamos a força de evitação

    def separation(self, mobs):
        steering = vec(0, 0)
        for mob in mobs:
            if mob != self:
                dist = self.pos.distance_to(mob.pos)
                if dist < 50:
                    diff = self.pos - mob.pos
                    diff.normalize_ip()
                    steering += diff / dist
        if steering.length() > 0:
            steering.scale_to_length(MAX_FORCE)
        return steering

    def alignment(self, mobs):
        steering = vec(0, 0)
        for mob in mobs:
            if mob != self:
                steering += mob.vel
        if len(mobs) > 1:
            steering /= len(mobs) - 1
            steering -= self.vel
            if steering.length() > MAX_FORCE:
                steering.scale_to_length(MAX_FORCE)
        return steering

    def cohesion(self, mobs):
        center = vec(0, 0)
        for mob in mobs:
            if mob != self:
                center += mob.pos
        if len(mobs) > 1:
            center /= len(mobs) - 1
            return self.seek_with_approach(center)
        return vec(0, 0)

    def update(self):
        seek_force = self.seek_with_approach(target_pos) * 0.5
        avoid_force = self.avoid_obstacles(walls) * 1.5
        sep_force = self.separation(mobs) * 1.5
        ali_force = self.alignment(mobs) * 1.0
        coh_force = self.cohesion(mobs) * 1.0
        
        self.acc = seek_force + avoid_force + sep_force + ali_force + coh_force
        
        self.vel += self.acc
        if self.vel.length() > MAX_SPEED:
            self.vel.scale_to_length(MAX_SPEED)
        self.pos += self.vel
        
        # Colisão com as bordas da tela
        if self.pos.x < 0 or self.pos.x > WIDTH:
            self.vel.x *= -1
        if self.pos.y < 0 or self.pos.y > HEIGHT:
            self.vel.y *= -1
        
        self.pos.x = max(0, min(self.pos.x, WIDTH))
        self.pos.y = max(0, min(self.pos.y, HEIGHT))
        
        self.rect.center = self.pos

    def draw_vectors(self):
        scale = 25
        pg.draw.line(screen, GREEN, self.pos, (self.pos + self.vel * scale), 5)
        pg.draw.line(screen, RED, self.pos, (self.pos + self.acc * scale * 5), 5)

# Inicialização do Pygame
pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
clock = pg.time.Clock()

all_sprites = pg.sprite.Group()
walls = pg.sprite.Group()
mobs = pg.sprite.Group()

# Criação de mobs
for _ in range(20):  # Cria 20 Mobs
    Mob()

# Criação das paredes para formar um gargalo estreito
wall_width = 32
gap_size = 1  # Tamanho do vão em unidades de parede (1 para um quadrado, 0.5 para meio quadrado)
gap_start = HEIGHT // 2 - (gap_size * wall_width) // 2
gap_end = gap_start + gap_size * wall_width

for y in range(0, HEIGHT, wall_width):
    if y < gap_start or y >= gap_end:
        Wall(WIDTH // 2 // wall_width, y // wall_width)

# Definir o alvo fixo
target_pos = vec(WIDTH - 100, HEIGHT // 2)

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
            if event.button == 3:
                for sprite in all_sprites:
                    if sprite.rect.collidepoint(event.pos):
                        sprite.kill()

    if not paused:
        all_sprites.update()
    pg.display.set_caption("{:.2f}".format(clock.get_fps()))
    screen.fill(DARKGRAY)
    all_sprites.draw(screen)
    if show_vectors:
        for sprite in all_sprites:
            sprite.draw_vectors()
    
    # Desenhar o alvo
    pg.draw.circle(screen, RED, (int(target_pos.x), int(target_pos.y)), 10)
    
    pg.display.flip()

pg.quit()