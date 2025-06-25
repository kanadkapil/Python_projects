import pygame
import random
import sys
import os

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# --- Game Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SPEED = 5

# Base difficulty parameters (will increase with levels)
BASE_BULLET_SPEED = 10
BASE_ENEMY_SPEED_X = 1.0
BASE_ENEMY_SPEED_Y = 25
BASE_ENEMY_BULLET_SPEED = 6
BASE_ENEMY_SHOOT_PROB = 0.001 # Reduced initial probability for enemy to shoot

# Difficulty scaling factors per level
ENEMY_SPEED_X_INCREMENT = 0.1
ENEMY_BULLET_SPEED_INCREMENT = 0.2
ENEMY_SHOOT_PROB_INCREMENT = 0.0002
ENEMY_ROWS_INCREMENT_PER_LEVEL = 0 # No extra rows by default, adjust if needed
MAX_ENEMY_ROWS = 7 # Cap for enemy rows

# Mystery Ship (UFO) parameters
MYSTERY_SHIP_APPEAR_PROB = 0.0005 # Probability per frame for UFO to appear
MYSTERY_SHIP_SPEED = 3
MYSTERY_SHIP_POINTS = 100 # Points for shooting the UFO

# Shield parameters
SHIELD_BLOCK_SIZE = 10
SHIELD_HP = 4 # How many hits a single shield block can take (more for stronger shields)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 150, 255)
YELLOW = (255, 255, 0)
GREY = (100, 100, 100)
LIGHT_BLUE = (173, 216, 230)
SHIELD_COLOR = (0, 100, 0) # Dark green for shields

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
player_shoot_sound = None
enemy_explosion_sound = None
player_hit_sound = None
level_up_sound = None
mystery_ship_sound = None # New sound for UFO
mystery_ship_explode_sound = None # New sound for UFO explosion

try:
    script_dir = os.path.dirname(__file__)
    player_shoot_sound = pygame.mixer.Sound(os.path.join(script_dir, 'laser.wav'))
    enemy_explosion_sound = pygame.mixer.Sound(os.path.join(script_dir, 'explosion.wav'))
    player_hit_sound = pygame.mixer.Sound(os.path.join(script_dir, 'hit.wav'))
    level_up_sound = pygame.mixer.Sound(os.path.join(script_dir, 'levelup.wav'))
    mystery_ship_sound = pygame.mixer.Sound(os.path.join(script_dir, 'ufo_highpitch.wav')) # UFO flying sound
    mystery_ship_explode_sound = pygame.mixer.Sound(os.path.join(script_dir, 'ufo_lowpitch.wav')) # UFO explosion sound
except (FileNotFoundError, pygame.error) as e:
    print(f"Error loading sound files: {e}. Sounds will be disabled.")

# --- Starfield background variables ---
stars = []
for _ in range(200):
    x = random.randint(0, SCREEN_WIDTH)
    y = random.randint(0, SCREEN_HEIGHT)
    size = random.randint(1, 3)
    stars.append((x, y, size))

# --- Classes ---

class Player(pygame.sprite.Sprite):
    """Represents the player's spaceship."""
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([50, 40], pygame.SRCALPHA)
        pygame.draw.polygon(self.image, GREEN, [(0, 40), (50, 40), (25, 0)])
        pygame.draw.rect(self.image, BLUE, (15, 35, 20, 10))
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 30

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.rect.x += PLAYER_SPEED
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

class Bullet(pygame.sprite.Sprite):
    """Represents a bullet fired by the player."""
    def __init__(self, x, y, speed):
        super().__init__()
        self.image = pygame.Surface([5, 15])
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = speed

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()

class EnemyBullet(pygame.sprite.Sprite):
    """Represents a bullet fired by an enemy."""
    def __init__(self, x, y, speed):
        super().__init__()
        self.image = pygame.Surface([8, 8])
        self.image.fill(YELLOW)
        pygame.draw.circle(self.image, RED, (4,4), 4)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    """Represents an enemy alien."""
    def __init__(self, x, y, speed_x, speed_y):
        super().__init__()
        self.image = pygame.Surface([40, 30], pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, RED, (0, 0, 40, 30))
        pygame.draw.rect(self.image, GREY, (10, 10, 20, 10))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = 1
        self.speed_x = speed_x
        self.speed_y = speed_y

    def update(self):
        self.rect.x += self.speed_x * self.direction
        if self.rect.right >= SCREEN_WIDTH or self.rect.left <= 0:
            self.direction *= -1
            self.rect.y += self.speed_y
            if self.rect.right >= SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH - 1
            if self.rect.left <= 0:
                self.rect.left = 1

class MysteryShip(pygame.sprite.Sprite):
    """Represents the high-value mystery ship (UFO)."""
    def __init__(self, speed):
        super().__init__()
        self.image = pygame.Surface([60, 30], pygame.SRCALPHA)
        # Simple UFO shape: two ellipses and a rectangle
        pygame.draw.ellipse(self.image, YELLOW, (0, 10, 60, 20)) # Main body
        pygame.draw.ellipse(self.image, GREY, (10, 0, 40, 15)) # Top dome
        self.rect = self.image.get_rect()
        # Randomly appear from left or right
        if random.choice([True, False]):
            self.rect.x = -self.rect.width # Start off left
            self.direction = 1
        else:
            self.rect.x = SCREEN_WIDTH # Start off right
            self.direction = -1
        self.rect.y = 20 # Appear near the top of the screen
        self.speed = speed

        if mystery_ship_sound:
            mystery_ship_sound.play(-1) # Loop indefinitely

    def update(self):
        self.rect.x += self.speed * self.direction
        if (self.direction == 1 and self.rect.left > SCREEN_WIDTH) or \
           (self.direction == -1 and self.rect.right < 0):
            self.kill() # Remove if goes off-screen
            if mystery_ship_sound:
                mystery_ship_sound.stop() # Stop sound when gone

class ShieldBlock(pygame.sprite.Sprite):
    """Represents a single destructible block of a shield."""
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([SHIELD_BLOCK_SIZE, SHIELD_BLOCK_SIZE])
        self.image.fill(SHIELD_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.hp = SHIELD_HP # Health points for the block

    def hit(self):
        self.hp -= 1
        if self.hp <= 0:
            self.kill() # Destroy block if HP runs out
        else:
            # Change color slightly to show damage
            damage_percent = (SHIELD_HP - self.hp) / SHIELD_HP
            current_color_value = max(0, int(SHIELD_COLOR[1] * (1 - damage_percent)))
            self.image.fill((SHIELD_COLOR[0], current_color_value, SHIELD_COLOR[2]))


# --- Game Variables & Groups ---
all_sprites = pygame.sprite.Group()
player_bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
mystery_ships = pygame.sprite.Group() # New group for UFO
shields = pygame.sprite.Group() # New group for shields

player = Player()
all_sprites.add(player)

score = 0
lives = 3
level = 1
game_state = "RUNNING" # Possible states: "RUNNING", "GAME_OVER", "YOU_WON", "LEVEL_CLEARED", "PAUSED"
level_clear_timer = 0
mystery_ship_timer = 0 # Timer to control UFO spawns

# Dynamic difficulty parameters (updated per level)
current_bullet_speed = BASE_BULLET_SPEED
current_enemy_speed_x = BASE_ENEMY_SPEED_X
current_enemy_speed_y = BASE_ENEMY_SPEED_Y
current_enemy_bullet_speed = BASE_ENEMY_BULLET_SPEED
current_enemy_shoot_prob = BASE_ENEMY_SHOOT_PROB

def calculate_difficulty_parameters(current_level):
    """Calculates game parameters based on the current level."""
    global current_bullet_speed, current_enemy_speed_x, current_enemy_speed_y, \
           current_enemy_bullet_speed, current_enemy_shoot_prob

    current_bullet_speed = BASE_BULLET_SPEED # Player bullet speed is constant
    current_enemy_speed_x = BASE_ENEMY_SPEED_X + (current_level - 1) * ENEMY_SPEED_X_INCREMENT
    current_enemy_speed_y = BASE_ENEMY_SPEED_Y
    current_enemy_bullet_speed = BASE_ENEMY_BULLET_SPEED + (current_level - 1) * ENEMY_BULLET_SPEED_INCREMENT
    current_enemy_shoot_prob = BASE_ENEMY_SHOOT_PROB + (current_level - 1) * ENEMY_SHOOT_PROB_INCREMENT
    current_enemy_shoot_prob = min(current_enemy_shoot_prob, 0.015) # Example cap

def spawn_enemies(rows, cols, x_offset=50, y_offset=50, x_padding=60, y_padding=50):
    """
    Spawns a grid of enemies with current difficulty parameters.
    """
    # Clear existing enemies and their bullets before spawning new wave
    enemies.empty()
    enemy_bullets.empty()
    # Remove enemies from all_sprites as well
    for sprite in all_sprites:
        if isinstance(sprite, Enemy) or isinstance(sprite, EnemyBullet) or isinstance(sprite, MysteryShip):
            sprite.kill()
    if mystery_ship_sound: # Stop UFO sound if any is active
        mystery_ship_sound.stop()

    actual_rows = min(rows + (level - 1) * ENEMY_ROWS_INCREMENT_PER_LEVEL, MAX_ENEMY_ROWS)

    for row in range(actual_rows):
        for col in range(cols):
            enemy = Enemy(x_offset + col * x_padding, y_offset + row * y_padding,
                          current_enemy_speed_x, current_enemy_speed_y)
            all_sprites.add(enemy)
            enemies.add(enemy)

def create_shields(num_shields=4, shield_base_y=SCREEN_HEIGHT - 100):
    """Creates a set of destructible shields."""
    shield_width = SHIELD_BLOCK_SIZE * 5 # Example width for a single shield
    gap_between_shields = (SCREEN_WIDTH - (num_shields * shield_width)) // (num_shields + 1)
    
    # Clear existing shields
    shields.empty()
    for sprite in all_sprites:
        if isinstance(sprite, ShieldBlock):
            sprite.kill()

    for i in range(num_shields):
        start_x = (i + 1) * gap_between_shields + i * shield_width
        # Create a simple block-based shield shape
        # You can customize these block patterns for different shield shapes
        shield_structure = [
            (0,0), (1,0), (2,0), (3,0), (4,0),
            (0,1), (1,1), (2,1), (3,1), (4,1),
            (0,2), (1,2), (3,2), (4,2), # Gap in middle
            (0,3), (4,3) # Bottom corner blocks
        ]
        for dx, dy in shield_structure:
            block = ShieldBlock(start_x + dx * SHIELD_BLOCK_SIZE, shield_base_y + dy * SHIELD_BLOCK_SIZE)
            all_sprites.add(block)
            shields.add(block)


# Initial setup for level 1
calculate_difficulty_parameters(level)
spawn_enemies(5, 10) # Starting with 5 rows of enemies
create_shields() # Create shields at the start of the game

# Function to draw text message boxes
def draw_message_box(message, color, font_obj, y_offset_factor=0):
    """Draws a centered message box on the screen."""
    text_surface = font_obj.render(message, True, color)
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + y_offset_factor))

    box_padding = 20
    box_rect = text_rect.inflate(box_padding * 2, box_padding * 2)
    pygame.draw.rect(screen, BLACK, box_rect, border_radius=10)
    pygame.draw.rect(screen, color, box_rect, 3, border_radius=10)

    screen.blit(text_surface, text_rect)

# Function to draw visual lives indicator
def draw_lives(surface, x, y, lives_count):
    """Draws small player icons for each remaining life."""
    for i in range(lives_count):
        # Create a miniature player ship image
        life_icon = pygame.Surface([25, 20], pygame.SRCALPHA)
        pygame.draw.polygon(life_icon, GREEN, [(0, 20), (25, 20), (12.5, 0)])
        surface.blit(life_icon, (x + i * 30, y))

# --- Game Loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_state == "RUNNING":
                bullet = Bullet(player.rect.centerx, player.rect.top, current_bullet_speed)
                all_sprites.add(bullet)
                player_bullets.add(bullet)
                if player_shoot_sound:
                    player_shoot_sound.play()

            # Toggle pause
            if event.key == pygame.K_p:
                if game_state == "RUNNING":
                    game_state = "PAUSED"
                elif game_state == "PAUSED":
                    game_state = "RUNNING"

            if event.key == pygame.K_r and (game_state == "GAME_OVER" or game_state == "YOU_WON"):
                # Reset game state
                game_state = "RUNNING"
                score = 0
                lives = 3
                level = 1
                calculate_difficulty_parameters(level)
                all_sprites.empty()
                player_bullets.empty()
                enemies.empty()
                enemy_bullets.empty()
                mystery_ships.empty()
                shields.empty() # Clear shields on restart

                player = Player()
                all_sprites.add(player)
                spawn_enemies(5, 10)
                create_shields() # Recreate shields on restart


    if game_state == "RUNNING":
        # Update sprites
        all_sprites.update()

        # Mystery Ship spawn logic
        if not mystery_ships and random.random() < MYSTERY_SHIP_APPEAR_PROB:
            ufo = MysteryShip(MYSTERY_SHIP_SPEED)
            all_sprites.add(ufo)
            mystery_ships.add(ufo)

        # Enemy shooting logic
        for enemy in enemies:
            if random.random() < current_enemy_shoot_prob:
                enemy_bullet = EnemyBullet(enemy.rect.centerx, enemy.rect.bottom, current_enemy_bullet_speed)
                all_sprites.add(enemy_bullet)
                enemy_bullets.add(enemy_bullet)

        # --- Collision Detection ---

        # Player Bullet-Enemy collision
        collisions = pygame.sprite.groupcollide(player_bullets, enemies, True, True)
        for bullet, enemy_list in collisions.items():
            for enemy in enemy_list:
                score += 10
                if enemy_explosion_sound:
                    enemy_explosion_sound.play()

        # Player Bullet-Mystery Ship collision
        mystery_ship_hits = pygame.sprite.groupcollide(player_bullets, mystery_ships, True, True)
        for bullet, ufo_list in mystery_ship_hits.items():
            for ufo in ufo_list:
                score += MYSTERY_SHIP_POINTS # Bonus points
                if mystery_ship_explode_sound:
                    mystery_ship_explode_sound.play()
                if mystery_ship_sound:
                    mystery_ship_sound.stop() # Stop flying sound

        # Enemy Bullet-Player collision
        player_hit_by_bullet = pygame.sprite.spritecollide(player, enemy_bullets, True)
        if player_hit_by_bullet:
            lives -= 1
            if player_hit_sound:
                player_hit_sound.play()
            if lives <= 0:
                game_state = "GAME_OVER"

        # Player-Enemy collision (if enemies reach player's level or below)
        if pygame.sprite.spritecollide(player, enemies, False):
            game_state = "GAME_OVER"

        # Check if any enemy reached the bottom of the screen
        for enemy in enemies:
            if enemy.rect.bottom >= SCREEN_HEIGHT:
                game_state = "GAME_OVER"
                break

        # Check if all enemies are defeated for current level
        if not enemies:
            game_state = "LEVEL_CLEARED"
            level_clear_timer = pygame.time.get_ticks()
            if level_up_sound:
                level_up_sound.play()

        # --- Shield Collisions ---
        # Player bullets hitting shields
        bullet_shield_collisions = pygame.sprite.groupcollide(player_bullets, shields, True, False) # Bullet removed, shield takes damage
        for bullet, shield_blocks in bullet_shield_collisions.items():
            for block in shield_blocks:
                block.hit() # Decrement shield block HP

        # Enemy bullets hitting shields
        enemy_bullet_shield_collisions = pygame.sprite.groupcollide(enemy_bullets, shields, True, False) # Bullet removed, shield takes damage
        for bullet, shield_blocks in enemy_bullet_shield_collisions.items():
            for block in shield_blocks:
                block.hit() # Decrement shield block HP


    elif game_state == "LEVEL_CLEARED":
        draw_message_box(f"Level {level} Complete!", LIGHT_BLUE, font_large, y_offset_factor=-50)
        draw_message_box("Preparing for next wave...", WHITE, font_medium, y_offset_factor=0)

        current_time = pygame.time.get_ticks()
        if current_time - level_clear_timer > 3000:
            level += 1
            calculate_difficulty_parameters(level)
            spawn_enemies(5, 10) # Respawn initial enemies for next level
            create_shields() # Recreate shields for new level
            game_state = "RUNNING"


    # --- Drawing ---
    screen.fill(BLACK)

    # Draw starfield background
    for x, y, size in stars:
        pygame.draw.circle(screen, WHITE, (x, y), size)

    # Only draw sprites if game is running or if it's game over/you won
    if game_state == "RUNNING" or game_state == "GAME_OVER" or game_state == "YOU_WON" or game_state == "PAUSED":
        all_sprites.draw(screen)

    # Display score, lives, and level
    score_text = font_small.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    level_text = font_small.render(f"Level: {level}", True, WHITE)
    level_text_rect = level_text.get_rect(center=(SCREEN_WIDTH // 2, 10 + level_text.get_height() // 2))
    screen.blit(level_text, level_text_rect)

    draw_lives(screen, SCREEN_WIDTH - 100, 10, lives) # Draw visual lives

    # Display Game Over / You Won / Level Clear / Paused message
    if game_state == "GAME_OVER":
        draw_message_box("GAME OVER!", RED, font_large, y_offset_factor=-50)
        draw_message_box(f"Final Score: {score}", WHITE, font_medium, y_offset_factor=0)
        restart_text = font_medium.render("Press 'R' to Restart", True, BLUE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        screen.blit(restart_text, restart_rect)

    elif game_state == "YOU_WON":
        draw_message_box("YOU WON!", GREEN, font_large, y_offset_factor=-50)
        draw_message_box(f"Final Score: {score}", WHITE, font_medium, y_offset_factor=0)
        restart_text = font_medium.render("Press 'R' to Restart", True, BLUE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        screen.blit(restart_text, restart_rect)

    elif game_state == "PAUSED":
        draw_message_box("PAUSED", YELLOW, font_large, y_offset_factor=-50)
        draw_message_box("Press 'P' to Resume", WHITE, font_medium, y_offset_factor=0)

    pygame.display.flip()

    clock.tick(FPS)

pygame.quit()
sys.exit()
