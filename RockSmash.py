import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple Rock Shooter")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Rocket class
class Rocket(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 30))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT - 50)

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= 5
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += 5
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= 5
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += 5

# Rock class
class Rock(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - 40)
        self.rect.y = random.randint(-100, -40)
        self.speed = random.randint(2, 5)  # Different speeds

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()  # Remove rock when it goes off screen

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.rect.y -= 10
        if self.rect.bottom < 0:
            self.kill()

# Initialize sprite groups
all_sprites = pygame.sprite.Group()
rocks = pygame.sprite.Group()
bullets = pygame.sprite.Group()

# Create the player rocket
rocket = Rocket()
all_sprites.add(rocket)

# Function to reset the game
def reset_game():
    global score
    score = 0
    for rock in rocks:
        rock.kill()
    for bullet in bullets:
        bullet.kill()
    for _ in range(random.randint(3, 4)):
        rock = Rock()
        all_sprites.add(rock)
        rocks.add(rock)

# Score
score = 0
font = pygame.font.SysFont("Arial", 24)

# Game loop
running = True
game_over = False
clock = pygame.time.Clock()
reset_game()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                bullet = Bullet(rocket.rect.centerx, rocket.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
            if event.key == pygame.K_r and game_over:
                game_over = False
                reset_game()

    # Update
    if not game_over:
        all_sprites.update()

        # Check for collisions
        if pygame.sprite.spritecollideany(rocket, rocks):
            game_over = True

        for bullet in bullets:
            hits = pygame.sprite.spritecollide(bullet, rocks, True)
            for hit in hits:
                score += 10
                rock = Rock()
                all_sprites.add(rock)
                rocks.add(rock)
            if hits:
                bullet.kill()

    # Draw
    screen.fill(BLACK)
    all_sprites.draw(screen)

    # Draw score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # Game Over screen
    if game_over:
        game_over_text = font.render("Game Over! Press 'R' to Restart or 'Q' to Quit", True, WHITE)
        screen.blit(game_over_text, (WIDTH // 2 - 250, HEIGHT // 2))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
