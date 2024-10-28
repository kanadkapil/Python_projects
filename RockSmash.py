import pygame
import random
import os

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Enhanced Rock Shooter")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Sound setup
pygame.mixer.init()

# Helper function to load sound and handle missing files
def load_sound(file):
    if os.path.isfile(file):
        return pygame.mixer.Sound(file)
    return None

# Load sounds (they’ll be None if files are missing)
shoot_sound = load_sound("shoot.wav")
explosion_sound = load_sound("explosion.wav")
game_over_sound = load_sound("game_over.wav")
if os.path.isfile("background_music.mp3"):
    pygame.mixer.music.load("background_music.mp3")
    pygame.mixer.music.play(-1)

class Rocket(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 30))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        self.lives = 3
        self.speed = 5

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed

class Rock(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image = pygame.Surface((random.randint(30, 50), random.randint(30, 50)))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.y -= 10
        if self.rect.bottom < 0:
            self.kill()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, effect_type):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.effect_type = effect_type
        if effect_type == "extra_life":
            self.image.fill(BLUE)
        elif effect_type == "speed_boost":
            self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=(random.randint(0, WIDTH), random.randint(-100, -40)))
        self.speed = 2

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

# Initialize game variables
score = 0
level = 1
font = pygame.font.SysFont("Arial", 24)

# Initialize sprite groups
all_sprites = pygame.sprite.Group()
rocks = pygame.sprite.Group()
bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()

rocket = Rocket()
all_sprites.add(rocket)

# Set timers
ROCK_EVENT = pygame.USEREVENT + 1
POWERUP_EVENT = pygame.USEREVENT + 2
pygame.time.set_timer(ROCK_EVENT, 1000)
pygame.time.set_timer(POWERUP_EVENT, 10000)

def reset_game():
    global score, level
    score = 0
    level = 1
    rocket.lives = 3
    rocket.speed = 5
    rocks.empty()
    bullets.empty()
    powerups.empty()

# Game loop
running = True
game_over = False
clock = pygame.time.Clock()
reset_game()

while running:
    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                bullet = Bullet(rocket.rect.centerx, rocket.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                if shoot_sound:
                    shoot_sound.play()
            if event.key == pygame.K_r and game_over:
                game_over = False
                reset_game()
            if event.key == pygame.K_q and game_over:
                running = False
        elif event.type == ROCK_EVENT and not game_over:
            spawn_rate = max(1000 - level * 50, 200)
            pygame.time.set_timer(ROCK_EVENT, spawn_rate)
            rock = Rock(random.randint(2, 5 + level))
            all_sprites.add(rock)
            rocks.add(rock)
        elif event.type == POWERUP_EVENT and not game_over:
            effect_type = random.choice(["extra_life", "speed_boost"])
            powerup = PowerUp(effect_type)
            all_sprites.add(powerup)
            powerups.add(powerup)

    if not game_over:
        all_sprites.update()

        # Collision detection for rocket and rocks
        if pygame.sprite.spritecollideany(rocket, rocks):
            if explosion_sound:
                explosion_sound.play()
            rocket.lives -= 1
            if rocket.lives <= 0:
                game_over = True
                if game_over_sound:
                    game_over_sound.play()

        # Collision detection for bullets and rocks
        for bullet in bullets:
            hits = pygame.sprite.spritecollide(bullet, rocks, True)
            if hits:
                score += 10
                bullet.kill()
                if explosion_sound:
                    explosion_sound.play()
                if score % 50 == 0:
                    level += 1

        # Power-up collection
        for powerup in pygame.sprite.spritecollide(rocket, powerups, True):
            if powerup.effect_type == "extra_life":
                rocket.lives += 1
            elif powerup.effect_type == "speed_boost":
                rocket.speed += 2

    # Draw everything
    screen.fill(BLACK)
    all_sprites.draw(screen)
    score_text = font.render(f"Score: {score}", True, WHITE)
    lives_text = font.render(f"Lives: {rocket.lives}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (10, 40))
    screen.blit(level_text, (10, 70))

    if game_over:
        game_over_text = font.render("Game Over! Press 'R' to Restart or 'Q' to Quit", True, WHITE)
        screen.blit(game_over_text, (WIDTH // 2 - 250, HEIGHT // 2))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
