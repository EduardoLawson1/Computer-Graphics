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
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
DARKGRAY = (40, 40, 40)
LIGHTGRAY = (140, 140, 140)

# Propriedades do Mob
MOB_SIZE = 16
MAX_SPEED = 4
MAX_FORCE = 0.3
APPROACH_RADIUS = 120
WALL_LIMIT = 20
SEPARATION_RADIUS = 30

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
    def __init__(self, x, y, color, target, group):
        self.groups = all_sprites, mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = pg.Surface((MOB_SIZE, MOB_SIZE))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.pos = vec(x, y)
        self.vel = vec(MAX_SPEED, 0).rotate(uniform(0, 360))
        self.acc = vec(0, 0)
        self.rect.center = self.pos
        self.target = target
        self.group = group
        self.reached_target = False

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
        return steer * 2

    def separation(self, mobs):
        steering = vec(0, 0)
        for mob in mobs:
            if mob != self:
                dist = self.pos.distance_to(mob.pos)
                if dist < SEPARATION_RADIUS:
                    diff = self.pos - mob.pos
                    diff.normalize_ip()
                    steering += diff / dist
        if steering.length() > 0:
            steering.scale_to_length(MAX_FORCE)
        return steering

    def alignment(self, mobs):
        steering = vec(0, 0)
        for mob in mobs:
            if mob != self and mob.group == self.group:
                steering += mob.vel
        if len(mobs) > 1:
            steering /= len(mobs) - 1
            steering -= self.vel
            if steering.length() > MAX_FORCE:
                steering.scale_to_length(MAX_FORCE)
        return steering

    def cohesion(self, mobs):
        center = vec(0, 0)
        count = 0
        for mob in mobs:
            if mob != self and mob.group == self.group:
                center += mob.pos
                count += 1
        if count > 0:
            center /= count
            return self.seek_with_approach(center)
        return vec(0, 0)

    def update(self):
        if not self.reached_target:
            seek_force = self.seek_with_approach(self.target) * 1.0
        else:
            seek_force = vec(0, 0)

        avoid_force = self.avoid_obstacles(walls) * 1.5
        sep_force = self.separation(mobs) * 2.0  # Increased separation force
        ali_force = self.alignment(mobs) * 1.0
        coh_force = self.cohesion(mobs) * 1.0
        
        self.acc = seek_force + avoid_force + sep_force + ali_force + coh_force
        
        self.vel += self.acc
        if self.vel.length() > MAX_SPEED:
            self.vel.scale_to_length(MAX_SPEED)
        self.pos += self.vel
        
        # Check if target is reached
        if self.pos.distance_to(self.target) < APPROACH_RADIUS:
            self.reached_target = True

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
mobs = pg.sprite.Group()
walls = pg.sprite.Group()

# Criação da parede central com um pequeno vão
wall_width = 32
gap_size = 3  # Tamanho do vão em unidades de parede
gap_start = HEIGHT // 2 - (gap_size * wall_width) // 2
gap_end = gap_start + gap_size * wall_width

for y in range(0, HEIGHT, wall_width):
    if y < gap_start or y >= gap_end:
        Wall(WIDTH // 2 // wall_width, y // wall_width)

# Criação de dois grupos de mobs
group1_target = vec(WIDTH - 50, HEIGHT // 2)
group2_target = vec(50, HEIGHT // 2)

for _ in range(10):
    Mob(randint(0, WIDTH // 4), randint(0, HEIGHT), YELLOW, group1_target, 1)
    Mob(randint(3 * WIDTH // 4, WIDTH), randint(0, HEIGHT), BLUE, group2_target, 2)

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

    if not paused:
        all_sprites.update()
    pg.display.set_caption("{:.2f}".format(clock.get_fps()))
    screen.fill(DARKGRAY)
    all_sprites.draw(screen)
    if show_vectors:
        for sprite in all_sprites:
            sprite.draw_vectors()
    
    # Desenhar os alvos
    pg.draw.circle(screen, RED, (int(group1_target.x), int(group1_target.y)), 10)
    pg.draw.circle(screen, RED, (int(group2_target.x), int(group2_target.y)), 10)
    
    pg.display.flip()

pg.quit()                                                                           