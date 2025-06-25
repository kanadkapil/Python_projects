import pygame
import random
import sys
import os # Import os for path handling for sounds

# Initialize Pygame
pygame.init()
pygame.mixer.init() # Initialize the mixer for sounds

# --- Game Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SPEED = 5
BULLET_SPEED = 10
ENEMY_SPEED_X = 1.5 # Slightly slower enemy movement for better control
ENEMY_SPEED_Y = 25  # How much enemies move down after hitting a side
ENEMY_BULLET_SPEED = 7
ENEMY_SHOOT_PROB = 0.005 # Probability per frame for an enemy to shoot

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 150, 255) # A softer blue
YELLOW = (255, 255, 0)
GREY = (100, 100, 100)

# Setup the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders")

# Clock for controlling frame rate
clock = pygame.time.Clock()
FPS = 60

# Fonts
font_small = pygame.font.Font(None, 30)
font_medium = pygame.font.Font(None, 40)
font_large = pygame.font.Font(None, 74)

# --- Sounds ---
# If you have actual sound files, place them in the same directory as this script
# and replace 'sound_file.wav' with your file names.
# If files are not found, sounds will be disabled to prevent crashes.

player_shoot_sound = None
enemy_explosion_sound = None
player_hit_sound = None

try:
    # Attempt to load actual sound files
    script_dir = os.path.dirname(__file__)
    player_shoot_sound = pygame.mixer.Sound(os.path.join(script_dir, 'laser.wav'))
    enemy_explosion_sound = pygame.mixer.Sound(os.path.join(script_dir, 'explosion.wav'))
    player_hit_sound = pygame.mixer.Sound(os.path.join(script_dir, 'hit.wav'))
except (FileNotFoundError, pygame.error) as e:
    print(f"Error loading sound files: {e}. Sounds will be disabled.")
    # If files are not found or there's a pygame error, keep sounds as None.
    # The game logic will check if sound objects exist before trying to play them.

# --- Starfield background variables ---
stars = []
for _ in range(200): # Number of stars
    x = random.randint(0, SCREEN_WIDTH)
    y = random.randint(0, SCREEN_HEIGHT)
    size = random.randint(1, 3)
    stars.append((x, y, size))

# --- Classes ---

class Player(pygame.sprite.Sprite):
    """
    Represents the player's spaceship.
    """
    def __init__(self):
        super().__init__()
        # Create a more stylized player ship (a triangle with a base)
        self.image = pygame.Surface([50, 40], pygame.SRCALPHA) # SRCALPHA for transparency
        pygame.draw.polygon(self.image, GREEN, [(0, 40), (50, 40), (25, 0)]) # Main body
        pygame.draw.rect(self.image, BLUE, (15, 35, 20, 10)) # Engine
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 30

    def update(self):
        """
        Updates the player's position based on keyboard input.
        """
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.rect.x += PLAYER_SPEED

        # Keep player within screen bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

class Bullet(pygame.sprite.Sprite):
    """
    Represents a bullet fired by the player.
    """
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([5, 15])
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y

    def update(self):
        """
        Moves the bullet upwards.
        Removes the bullet if it goes off-screen.
        """
        self.rect.y -= BULLET_SPEED
        if self.rect.bottom < 0:
            self.kill() # Remove the sprite from all groups

class EnemyBullet(pygame.sprite.Sprite):
    """
    Represents a bullet fired by an enemy.
    """
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([8, 8]) # Slightly larger, square bullet
        self.image.fill(YELLOW)
        pygame.draw.circle(self.image, RED, (4,4), 4) # Red center dot
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y

    def update(self):
        """
        Moves the enemy bullet downwards.
        Removes the bullet if it goes off-screen.
        """
        self.rect.y += ENEMY_BULLET_SPEED
        if self.rect.top > SCREEN_HEIGHT:
            self.kill() # Remove the sprite from all groups

class Enemy(pygame.sprite.Sprite):
    """
    Represents an enemy alien.
    """
    def __init__(self, x, y):
        super().__init__()
        # Create a more alien-like shape (a squashed octagon/diamond)
        self.image = pygame.Surface([40, 30], pygame.SRCALPHA)
        # Draw a shape resembling a classic invader
        pygame.draw.ellipse(self.image, RED, (0, 0, 40, 30))
        pygame.draw.rect(self.image, GREY, (10, 10, 20, 10)) # A small window/body detail
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = 1 # 1 for right, -1 for left

    def update(self):
        """
        Moves the enemy horizontally. If it hits the screen edge,
        it changes direction and moves down.
        """
        self.rect.x += ENEMY_SPEED_X * self.direction

        # Check for screen edges
        if self.rect.right >= SCREEN_WIDTH or self.rect.left <= 0:
            self.direction *= -1 # Reverse direction
            self.rect.y += ENEMY_SPEED_Y # Move down
            # If enemies move too far down, they can get stuck at the edge.
            # Adjust their horizontal position slightly to ensure they are inside.
            if self.rect.right >= SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH - 1
            if self.rect.left <= 0:
                self.rect.left = 1

# --- Game Variables & Groups ---
all_sprites = pygame.sprite.Group()
player_bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

score = 0
lives = 3 # Player lives
game_state = "RUNNING" # Possible states: "RUNNING", "GAME_OVER", "YOU_WON"

# Function to spawn enemies
def spawn_enemies(rows, cols, x_offset=50, y_offset=50, x_padding=60, y_padding=50):
    """
    Spawns a grid of enemies.
    """
    for row in range(rows):
        for col in range(cols):
            enemy = Enemy(x_offset + col * x_padding, y_offset + row * y_padding)
            all_sprites.add(enemy)
            enemies.add(enemy)

# Initial enemy spawn
spawn_enemies(5, 10)

# Function to draw text message boxes
def draw_message_box(message, color, font_obj, y_offset_factor=0):
    """Draws a centered message box on the screen."""
    text_surface = font_obj.render(message, True, color)
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + y_offset_factor))

    # Draw a background rect for the message
    box_padding = 20
    box_rect = text_rect.inflate(box_padding * 2, box_padding * 2)
    pygame.draw.rect(screen, BLACK, box_rect, border_radius=10)
    pygame.draw.rect(screen, color, box_rect, 3, border_radius=10) # Border

    screen.blit(text_surface, text_rect)

# --- Game Loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_state == "RUNNING":
                bullet = Bullet(player.rect.centerx, player.rect.top)
                all_sprites.add(bullet)
                player_bullets.add(bullet)
                if player_shoot_sound: # Play sound only if loaded (not None)
                    player_shoot_sound.play()

            if event.key == pygame.K_r and (game_state == "GAME_OVER" or game_state == "YOU_WON"):
                # Reset game state
                game_state = "RUNNING"
                score = 0
                lives = 3
                # Clear all existing sprites
                all_sprites.empty()
                player_bullets.empty()
                enemies.empty()
                enemy_bullets.empty()
                # Re-add player and spawn new enemies
                player = Player()
                all_sprites.add(player)
                spawn_enemies(5, 10)

    if game_state == "RUNNING":
        # Update sprites
        all_sprites.update()

        # Enemy shooting logic
        for enemy in enemies:
            if random.random() < ENEMY_SHOOT_PROB: # Chance for enemy to shoot
                enemy_bullet = EnemyBullet(enemy.rect.centerx, enemy.rect.bottom)
                all_sprites.add(enemy_bullet)
                enemy_bullets.add(enemy_bullet)

        # --- Collision Detection ---

        # Player Bullet-Enemy collision
        collisions = pygame.sprite.groupcollide(player_bullets, enemies, True, True)
        for bullet, enemy_list in collisions.items():
            for enemy in enemy_list:
                score += 10 # Increase score for each enemy hit
                if enemy_explosion_sound: # Play sound only if loaded
                    enemy_explosion_sound.play()

        # Enemy Bullet-Player collision
        player_hit_by_bullet = pygame.sprite.spritecollide(player, enemy_bullets, True) # True: remove bullet on hit
        if player_hit_by_bullet:
            lives -= 1
            if player_hit_sound: # Play sound only if loaded
                player_hit_sound.play()
            if lives <= 0:
                game_state = "GAME_OVER"

        # Player-Enemy collision (if enemies reach player's level or below)
        # Check this after all other collisions to ensure enemies are still there
        if pygame.sprite.spritecollide(player, enemies, False): # False means don't kill enemy
            game_state = "GAME_OVER"

        # Check if any enemy reached the bottom of the screen
        for enemy in enemies:
            if enemy.rect.bottom >= SCREEN_HEIGHT:
                game_state = "GAME_OVER"
                break

        # Check if all enemies are defeated
        if not enemies and game_state == "RUNNING": # Ensure game hasn't ended already
            game_state = "YOU_WON"


    # --- Drawing ---
    screen.fill(BLACK) # Clear the screen each frame

    # Draw starfield background
    for x, y, size in stars:
        pygame.draw.circle(screen, WHITE, (x, y), size)

    all_sprites.draw(screen) # Draw all sprites

    # Display score and lives
    score_text = font_small.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    lives_text = font_small.render(f"Lives: {lives}", True, WHITE)
    screen.blit(lives_text, (SCREEN_WIDTH - lives_text.get_width() - 10, 10))


    # Display Game Over / You Won message
    if game_state == "GAME_OVER":
        draw_message_box("GAME OVER!", RED, font_large, y_offset_factor=-50)
        draw_message_box(f"Final Score: {score}", WHITE, font_medium, y_offset_factor=0) # Display final score inside box
        restart_text = font_medium.render("Press 'R' to Restart", True, BLUE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        screen.blit(restart_text, restart_rect)

    elif game_state == "YOU_WON":
        draw_message_box("YOU WON!", GREEN, font_large, y_offset_factor=-50)
        draw_message_box(f"Final Score: {score}", WHITE, font_medium, y_offset_factor=0)
        restart_text = font_medium.render("Press 'R' to Restart", True, BLUE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        screen.blit(restart_text, restart_rect)

    pygame.display.flip() # Update the full display Surface to the screen

    # Cap the frame rate
    clock.tick(FPS)

pygame.quit()
sys.exit()
