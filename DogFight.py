import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Fighter Jet Dogfight")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Clock
clock = pygame.time.Clock()
FPS = 60

# Load fonts
font = pygame.font.SysFont(None, 30)

# Jet settings
JET_SIZE = (50, 40)
JET_SPEED = 5
MISSILE_SPEED = 8
BULLET_SPEED = 12
MAX_MISSILES = 3
MAX_HEALTH = 100


def draw_text(text, x, y, color=WHITE):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


class Jet:
    def __init__(self, x, y, color, is_player=True):
        self.rect = pygame.Rect(x, y, *JET_SIZE)
        self.color = color
        self.speed = JET_SPEED
        self.health = MAX_HEALTH
        self.missiles = MAX_MISSILES
        self.is_player = is_player
        self.angle = 0
        self.bullets = []
        self.missiles_list = []

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        for bullet in self.bullets:
            pygame.draw.circle(screen, WHITE, (bullet.x, bullet.y), 4)
        for missile in self.missiles_list:
            pygame.draw.circle(screen, RED, (missile.x, missile.y), 6)

    def move(self, keys=None, target=None):
        if self.is_player:
            if keys[pygame.K_LEFT]:
                self.rect.x -= self.speed
            if keys[pygame.K_RIGHT]:
                self.rect.x += self.speed
            if keys[pygame.K_UP]:
                self.rect.y -= self.speed
            if keys[pygame.K_DOWN]:
                self.rect.y += self.speed
        else:
            if target:
                dx = target.rect.centerx - self.rect.centerx
                dy = target.rect.centery - self.rect.centery
                dist = math.hypot(dx, dy)
                if dist != 0:
                    self.rect.x += int(dx / dist * self.speed * 0.6)
                    self.rect.y += int(dy / dist * self.speed * 0.6)
                if random.randint(0, 80) == 0:
                    self.fire_bullet()

    def fire_bullet(self):
        bullet = pygame.Rect(self.rect.centerx, self.rect.centery, 5, 5)
        self.bullets.append(bullet)

    def fire_missile(self, target):
        if self.missiles > 0:
            missile = pygame.Rect(self.rect.centerx, self.rect.centery, 6, 6)
            self.missiles_list.append({"rect": missile, "target": target})
            self.missiles -= 1

    def update_projectiles(self):
        for bullet in self.bullets[:]:
            bullet.x += BULLET_SPEED if self.is_player else -BULLET_SPEED
            if not screen.get_rect().contains(bullet):
                self.bullets.remove(bullet)

        for m in self.missiles_list[:]:
            target = m["target"]
            dx = target.rect.centerx - m["rect"].centerx
            dy = target.rect.centery - m["rect"].centery
            dist = math.hypot(dx, dy)
            if dist != 0:
                m["rect"].x += int(dx / dist * MISSILE_SPEED)
                m["rect"].y += int(dy / dist * MISSILE_SPEED)
            if not screen.get_rect().contains(m["rect"]):
                self.missiles_list.remove(m)

    def check_hits(self, enemy):
        for bullet in self.bullets[:]:
            if enemy.rect.colliderect(bullet):
                enemy.health -= 5
                self.bullets.remove(bullet)
        for m in self.missiles_list[:]:
            if enemy.rect.colliderect(m["rect"]):
                enemy.health -= 20
                self.missiles_list.remove(m)


# Game objects
player = Jet(100, HEIGHT//2, BLUE, is_player=True)
enemy = Jet(WIDTH-150, HEIGHT//2, GREEN, is_player=False)

# Main game loop
running = True
while running:
    clock.tick(FPS)
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    # Player actions
    player.move(keys)
    if keys[pygame.K_SPACE]:
        player.fire_bullet()
    if keys[pygame.K_m]:
        player.fire_missile(enemy)

    # Enemy actions
    enemy.move(target=player)

    # Update and check hits
    player.update_projectiles()
    enemy.update_projectiles()
    player.check_hits(enemy)
    enemy.check_hits(player)

    # Draw jets and HUD
    player.draw()
    enemy.draw()
    draw_text(f"Player Health: {player.health}", 10, 10)
    draw_text(f"Enemy Health: {enemy.health}", 10, 40)
    draw_text(f"Missiles: {player.missiles}", 10, 70)

    # Check for win/loss
    if player.health <= 0:
        draw_text("YOU LOSE!", WIDTH//2 - 100, HEIGHT//2, RED)
        pygame.display.update()
        pygame.time.delay(2000)
        break
    elif enemy.health <= 0:
        draw_text("YOU WIN!", WIDTH//2 - 100, HEIGHT//2, GREEN)
        pygame.display.update()
        pygame.time.delay(2000)
        break

    pygame.display.update()

pygame.quit()
