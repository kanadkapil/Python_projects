import pygame
import random
import math

# Initialize Pygame and Mixer
pygame.init()
pygame.mixer.init()

# Screen settings
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Fighter Jet Dogfight")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (30, 144, 255)
GREEN = (0, 255, 0)
SKY_BLUE = (135, 206, 235)

# Game settings
FPS = 60
JET_SIZE = (50, 40)
MAX_HEALTH = 100
BULLET_SPEED = 12
MISSILE_SPEED = 8
MAX_MISSILES = 3
MISSILE_LOCK_RANGE = 300

# Clock
clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont(None, 30)

# Load sounds (place .wav files in project directory)
try:
    bg_music = pygame.mixer.Sound("bgmusic.wav")
    gunfire_sound = pygame.mixer.Sound("gunfire.wav")
    missile_sound = pygame.mixer.Sound("missile_launch.wav")
    jet_move_sound = pygame.mixer.Sound("jet_move.wav")
    jet_destroyed_sound = pygame.mixer.Sound("jet_destroyed.wav")

    bg_music.set_volume(0.3)
    bg_music.play(-1)
except:
    print("Sound files not found. Continuing without sound.")

def draw_text(text, x, y, color=WHITE):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def draw_health_bar(x, y, health, color):
    pygame.draw.rect(screen, RED, (x, y, 100, 10))
    pygame.draw.rect(screen, color, (x, y, max(0, health), 10))

class Cloud:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed

    def move(self):
        self.x -= self.speed
        if self.x < -100:
            self.x = WIDTH + random.randint(0, 300)
            self.y = random.randint(50, HEIGHT - 100)

    def draw(self):
        pygame.draw.ellipse(screen, WHITE, (self.x, self.y, 60, 40))
        pygame.draw.ellipse(screen, WHITE, (self.x + 30, self.y - 10, 50, 50))
        pygame.draw.ellipse(screen, WHITE, (self.x + 50, self.y, 60, 40))

class Jet:
    def __init__(self, x, y, color, is_player=True):
        self.rect = pygame.Rect(x, y, *JET_SIZE)
        self.color = color
        self.speed = 5
        self.health = MAX_HEALTH
        self.missiles = MAX_MISSILES
        self.bullets = []
        self.missiles_list = []
        self.is_player = is_player

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        for bullet in self.bullets:
            pygame.draw.circle(screen, WHITE, (bullet.x, bullet.y), 4)
        for missile in self.missiles_list:
            pygame.draw.circle(screen, RED, (missile["rect"].x, missile["rect"].y), 6)

    def move(self, keys=None, target=None):
        if self.is_player:
            if keys[pygame.K_LEFT]: self.rect.x -= self.speed
            if keys[pygame.K_RIGHT]: self.rect.x += self.speed
            if keys[pygame.K_UP]: self.rect.y -= self.speed
            if keys[pygame.K_DOWN]: self.rect.y += self.speed
            if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or keys[pygame.K_UP] or keys[pygame.K_DOWN]:
                try: jet_move_sound.play(maxtime=100)
                except: pass
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
        try: gunfire_sound.play()
        except: pass

    def fire_missile(self, target):
        dx = target.rect.centerx - self.rect.centerx
        dy = target.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if self.missiles > 0 and dist <= MISSILE_LOCK_RANGE:
            missile = pygame.Rect(self.rect.centerx, self.rect.centery, 6, 6)
            self.missiles_list.append({"rect": missile, "target": target})
            self.missiles -= 1
            try: missile_sound.play()
            except: pass

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

    def is_behind(self, enemy):
        return self.rect.centerx < enemy.rect.centerx - 20

    def check_hits(self, enemy):
        for bullet in self.bullets[:]:
            if enemy.rect.colliderect(bullet):
                if self.is_player and self.is_behind(enemy):
                    enemy.health -= 5
                    self.bullets.remove(bullet)
                elif not self.is_player:
                    enemy.health -= 5
                    self.bullets.remove(bullet)

        for m in self.missiles_list[:]:
            if enemy.rect.colliderect(m["rect"]):
                enemy.health -= 20
                self.missiles_list.remove(m)

# Game Setup
player = Jet(100, HEIGHT//2, BLUE, is_player=True)
enemy = Jet(WIDTH-150, HEIGHT//2, GREEN, is_player=False)
clouds = [Cloud(random.randint(0, WIDTH), random.randint(50, HEIGHT - 150), random.uniform(0.5, 1.5)) for _ in range(6)]

# Main Game Loop
running = True
while running:
    clock.tick(FPS)
    screen.fill(SKY_BLUE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    # Move + Draw Clouds
    for cloud in clouds:
        cloud.move()
        cloud.draw()

    # Player actions
    player.move(keys)
    if keys[pygame.K_SPACE]:
        player.fire_bullet()
    if keys[pygame.K_m]:
        player.fire_missile(enemy)

    # Enemy AI
    enemy.move(target=player)

    # Update + Collision
    player.update_projectiles()
    enemy.update_projectiles()
    player.check_hits(enemy)
    enemy.check_hits(player)

    # Draw
    player.draw()
    enemy.draw()
    draw_health_bar(10, 10, player.health, BLUE)
    draw_health_bar(WIDTH - 110, 10, enemy.health, GREEN)
    draw_text(f"Missiles: {player.missiles}", 10, 30)

    # Lock-on UI
    dist = math.hypot(enemy.rect.centerx - player.rect.centerx, enemy.rect.centery - player.rect.centery)
    if dist <= MISSILE_LOCK_RANGE:
        draw_text("MISSILE LOCK!", WIDTH // 2 - 70, 30, RED)

    # Game over
    if player.health <= 0:
        try: jet_destroyed_sound.play()
        except: pass
        draw_text("YOU LOSE!", WIDTH // 2 - 100, HEIGHT // 2, RED)
        pygame.display.update()
        pygame.time.delay(2000)
        break
    elif enemy.health <= 0:
        try: jet_destroyed_sound.play()
        except: pass
        draw_text("YOU WIN!", WIDTH // 2 - 100, HEIGHT // 2, GREEN)
        pygame.display.update()
        pygame.time.delay(2000)
        break

    pygame.display.update()

pygame.quit()
