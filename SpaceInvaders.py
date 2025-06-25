import pygame
import random
import sys
import os

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# --- Game Constants ---
SCREEN_WIDTH = 1800
SCREEN_HEIGHT = 900
PLAYER_SPEED = 5
PLAYER_SAFE_ZONE_HEIGHT = 600 # Player can move within the bottom 600 pixels of the screen
PLAYER_FIRE_DELAY_NORMAL = 200 # milliseconds between shots
PLAYER_FIRE_DELAY_RAPID = 100 # milliseconds for rapid fire
PLAYER_INVINCIBILITY_DURATION = 2000 # milliseconds after being hit (for flicker)
PLAYER_RESPAWN_DELAY = 1500 # milliseconds before player reappears after losing a life

# Base difficulty parameters (will increase with levels)
BASE_BULLET_SPEED = 12
BASE_ENEMY_SPEED_X = 1.0
BASE_ENEMY_SPEED_Y = 25
BASE_ENEMY_BULLET_SPEED = 6
BASE_ENEMY_SHOOT_PROB = 0.001 # Reduced initial probability for enemy to shoot
ENEMY_DESCENT_SPEED = 1.5 # Speed at which enemies fly down during spawn animation

# Difficulty scaling factors per level
ENEMY_SPEED_X_INCREMENT = 0.1
ENEMY_BULLET_SPEED_INCREMENT = 0.2
ENEMY_SHOOT_PROB_INCREMENT = 0.0002
ENEMY_ROWS_INCREMENT_PER_LEVEL = 0 # No extra rows by default, adjust if needed
MAX_ENEMY_ROWS = 10 # Cap for enemy rows

# Enemy Score Tiers (points based on row from bottom to top)
# Example: If 5 rows, points for row 0 (bottom) to row 4 (top)
ENEMY_POINTS_TIERS = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100] # Max 10 tiers for MAX_ENEMY_ROWS

# Mystery Ship (UFO) parameters
MYSTERY_SHIP_APPEAR_PROB = 0.0005 # Probability per frame for UFO to appear
MYSTERY_SHIP_SPEED = 3
MYSTERY_SHIP_POINTS = 200 # Points for shooting the UFO (increased for high value)

# Shield parameters
SHIELD_BLOCK_SIZE = 10
SHIELD_HP = 4 # How many hits a single shield block can take (more for stronger shields)

# Power-up parameters
POWERUP_DROP_PROB_ENEMY = 0.05 # 5% chance for an enemy to drop a power-up
POWERUP_DROP_PROB_UFO = 0.8 # 80% chance for UFO to drop a power-up
POWERUP_SPEED = 3
RAPID_FIRE_DURATION = 7000 # milliseconds
SCORE_MULTIPLIER_DURATION = 10000 # milliseconds
SCORE_MULTIPLIER_VALUE = 2 # e.g., 2x points

# Floating Score parameters
FLOATING_SCORE_DURATION = 1500 # milliseconds
FLOATING_SCORE_SPEED = 0.5 # pixels per frame upwards

# Starfield parameters
STAR_SPEED = 0.5 # Speed at which stars scroll downwards

# High Score file
HIGH_SCORE_FILE = "highscore.txt"

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 150, 255)
YELLOW = (255, 255, 0)
GREY = (100, 100, 100)
LIGHT_BLUE = (173, 216, 230) # For level complete message
SHIELD_COLOR = (0, 100, 0) # Dark green for shields
POWERUP_COLORS = {
    "rapid_fire": (255, 0, 255), # Magenta
    "extra_life": (0, 255, 255), # Cyan
    "score_multiplier": (255, 165, 0) # Orange
}
EXPLOSION_COLORS = [(255, 165, 0, 255), (255, 255, 0, 255)] # Orange, Yellow for explosions


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
font_huge = pygame.font.Font(None, 120)

# --- Sounds ---
player_shoot_sound = None
enemy_explosion_sound = None
player_hit_sound = None
level_up_sound = None
mystery_ship_sound = None
mystery_ship_explode_sound = None
powerup_collect_sound = None
player_explode_sound = None

try:
    script_dir = os.path.dirname(__file__)
    # Add your .wav files to the same directory as this script!
    player_shoot_sound = pygame.mixer.Sound(os.path.join(script_dir, 'laser.wav'))
    enemy_explosion_sound = pygame.mixer.Sound(os.path.join(script_dir, 'explosion.wav'))
    player_hit_sound = pygame.mixer.Sound(os.path.join(script_dir, 'hit.wav'))
    level_up_sound = pygame.mixer.Sound(os.path.join(script_dir, 'levelup.wav'))
    mystery_ship_sound = pygame.mixer.Sound(os.path.join(script_dir, 'ufo_highpitch.wav'))
    mystery_ship_explode_sound = pygame.mixer.Sound(os.path.join(script_dir, 'ufo_lowpitch.wav'))
    powerup_collect_sound = pygame.mixer.Sound(os.path.join(script_dir, 'powerup.wav'))
    player_explode_sound = pygame.mixer.Sound(os.path.join(script_dir, 'player_explode.wav'))
except (FileNotFoundError, pygame.error) as e:
    print(f"Error loading sound files: {e}. Sounds will be disabled.")

# --- Starfield background variables ---
stars = []
for _ in range(200):
    x = random.randint(0, SCREEN_WIDTH)
    y = random.randint(0, SCREEN_HEIGHT)
    size = random.randint(1, 3)
    stars.append({'x': x, 'y': y, 'size': size})

# --- High Score Load/Save ---
def load_high_score():
    """Loads the high score from a file."""
    try:
        with open(HIGH_SCORE_FILE, "r") as f:
            return int(f.read())
    except (FileNotFoundError, ValueError):
        return 0 # Return 0 if file not found or invalid content

def save_high_score(score):
    """Saves the high score to a file."""
    with open(HIGH_SCORE_FILE, "w") as f:
        f.write(str(score))

high_score = load_high_score()

# --- Classes ---

class Player(pygame.sprite.Sprite):
    """Represents the player's spaceship."""
    def __init__(self):
        super().__init__()
        self.original_image = pygame.Surface([50, 40], pygame.SRCALPHA)
        pygame.draw.polygon(self.original_image, GREEN, [(0, 40), (50, 40), (25, 0)])
        pygame.draw.rect(self.original_image, BLUE, (15, 35, 20, 10))
        self.image = self.original_image.copy() # Current image for flicker
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 30
        self.last_hit_time = 0
        self.invincible = False
        self.visible = True # For respawn flicker

    def update(self):
        # Handle movement only if visible (not during explosion/respawn)
        if self.visible:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.rect.x -= PLAYER_SPEED
            if keys[pygame.K_RIGHT]:
                self.rect.x += PLAYER_SPEED
            if keys[pygame.K_UP]:
                self.rect.y -= PLAYER_SPEED
            if keys[pygame.K_DOWN]:
                self.rect.y += PLAYER_SPEED

            # Keep player within screen bounds (X-axis)
            if self.rect.left < 0:
                self.rect.left = 0
            if self.rect.right > SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH

            # Keep player within designated safe zone (Y-axis)
            player_top_bound = SCREEN_HEIGHT - PLAYER_SAFE_ZONE_HEIGHT
            if self.rect.top < player_top_bound:
                self.rect.top = player_top_bound
            if self.rect.bottom > SCREEN_HEIGHT:
                self.rect.bottom = SCREEN_HEIGHT

        # Invincibility flicker logic
        if self.invincible:
            # Flicker effect: make sprite semi-transparent every few frames
            alpha = 255 if pygame.time.get_ticks() // 100 % 2 == 0 else 100
            self.image.set_alpha(alpha)
            if pygame.time.get_ticks() - self.last_hit_time > PLAYER_INVINCIBILITY_DURATION:
                self.invincible = False
                self.image.set_alpha(255) # Restore full opacity


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
    def __init__(self, x, y, speed_x, speed_y, initial_y_target, row_index):
        super().__init__()
        self.image = pygame.Surface([40, 30], pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, RED, (0, 0, 40, 30))
        pygame.draw.rect(self.image, GREY, (10, 10, 20, 10))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y # Start at initial y (potentially above screen)
        self.direction = 1
        self.speed_x = speed_x
        self.speed_y = speed_y # This is the "drop" speed for zig-zag
        self.initial_y_target = initial_y_target # Target Y for spawn animation
        self.spawning = True # Flag for spawn animation state
        # Assign points based on row index (from bottom up)
        self.points = ENEMY_POINTS_TIERS[min(row_index, len(ENEMY_POINTS_TIERS) - 1)]

    def update(self):
        if self.spawning:
            # Move down until it reaches its intended row position
            if self.rect.y < self.initial_y_target:
                self.rect.y += ENEMY_DESCENT_SPEED
            else:
                self.rect.y = self.initial_y_target # Snap to target
                self.spawning = False # End spawning phase
        else:
            # Normal zig-zag movement
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
        pygame.draw.ellipse(self.image, YELLOW, (0, 10, 60, 20))
        pygame.draw.ellipse(self.image, GREY, (10, 0, 40, 15))
        self.rect = self.image.get_rect()
        if random.choice([True, False]):
            self.rect.x = -self.rect.width
            self.direction = 1
        else:
            self.rect.x = SCREEN_WIDTH
            self.direction = -1
        self.rect.y = 20
        self.speed = speed

        if mystery_ship_sound:
            mystery_ship_sound.play(-1)

    def update(self):
        self.rect.x += self.speed * self.direction
        if (self.direction == 1 and self.rect.left > SCREEN_WIDTH) or \
           (self.direction == -1 and self.rect.right < 0):
            self.kill()
            if mystery_ship_sound:
                mystery_ship_sound.stop()

class ShieldBlock(pygame.sprite.Sprite):
    """Represents a single destructible block of a shield."""
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([SHIELD_BLOCK_SIZE, SHIELD_BLOCK_SIZE])
        self.image.fill(SHIELD_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.hp = SHIELD_HP

    def hit(self):
        self.hp -= 1
        if self.hp <= 0:
            self.kill()
        else:
            damage_percent = (SHIELD_HP - self.hp) / SHIELD_HP
            current_color_value = max(0, int(SHIELD_COLOR[1] * (1 - damage_percent)))
            self.image.fill((SHIELD_COLOR[0], current_color_value, SHIELD_COLOR[2]))

class PowerUp(pygame.sprite.Sprite):
    """Represents a collectible power-up."""
    def __init__(self, x, y, p_type):
        super().__init__()
        self.type = p_type
        self.image = pygame.Surface([20, 20], pygame.SRCALPHA)
        self.color = POWERUP_COLORS.get(self.type, WHITE)
        pygame.draw.circle(self.image, self.color, (10, 10), 10)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.rect.y += POWERUP_SPEED
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    """Represents a visual explosion effect."""
    def __init__(self, center):
        super().__init__()
        self.size = 0
        self.image = pygame.Surface([60, 60], pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=center)
        self.frame = 0
        self.max_frame = 15
        self.color_fade_start = 5

    def update(self):
        self.frame += 1
        if self.frame > self.max_frame:
            self.kill()
            return

        self.image.fill((0, 0, 0, 0))
        self.size = int(30 * (self.frame / self.max_frame))

        if self.frame >= self.color_fade_start:
            alpha = max(0, 255 - int(255 * ((self.frame - self.color_fade_start) / (self.max_frame - self.color_fade_start))))
        else:
            alpha = 255

        current_color_base = random.choice(EXPLOSION_COLORS)
        current_color = (current_color_base[0], current_color_base[1], current_color_base[2], alpha)
        pygame.draw.circle(self.image, current_color, (30, 30), self.size)

class FloatingScore(pygame.sprite.Sprite):
    """Displays points earned briefly over a destroyed target."""
    def __init__(self, center, score_value):
        super().__init__()
        self.value = score_value
        self.font = font_medium
        self.color = WHITE
        self.image = self.font.render(str(self.value), True, self.color)
        self.rect = self.image.get_rect(center=center)
        self.start_time = pygame.time.get_ticks()

    def update(self):
        self.rect.y -= FLOATING_SCORE_SPEED
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time > FLOATING_SCORE_DURATION:
            self.kill()
        
        alpha = max(0, 255 - int(255 * ((current_time - self.start_time) / FLOATING_SCORE_DURATION)))
        self.image.set_alpha(alpha)


# --- Game Variables & Groups ---
all_sprites = pygame.sprite.Group()
player_bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
mystery_ships = pygame.sprite.Group()
shields = pygame.sprite.Group()
powerups = pygame.sprite.Group()
explosions = pygame.sprite.Group()
floating_scores = pygame.sprite.Group()

player = Player() # Player is now created as a global variable, but will be re-initialized by reset_game()

score = 0
lives = 3
level = 1
game_state = "MAIN_MENU" # Initial state is now MAIN_MENU
level_clear_timer = 0
last_shot_time = pygame.time.get_ticks()

# Power-up active states and timers
rapid_fire_active = False
rapid_fire_timer = 0
current_player_fire_delay = PLAYER_FIRE_DELAY_NORMAL

score_multiplier_active = False
score_multiplier_value = 1
score_multiplier_timer = 0

# Dynamic difficulty parameters (updated per level)
current_bullet_speed = BASE_BULLET_SPEED
current_enemy_speed_x = BASE_ENEMY_SPEED_X
current_enemy_speed_y = BASE_ENEMY_SPEED_Y
current_enemy_bullet_speed = BASE_ENEMY_BULLET_SPEED
current_enemy_shoot_prob = BASE_ENEMY_SHOOT_PROB

player_respawn_time = 0 # Time when player should respawn
player_is_dead = False # Flag for player death state

def calculate_difficulty_parameters(current_level):
    """Calculates game parameters based on the current level."""
    global current_bullet_speed, current_enemy_speed_x, current_enemy_speed_y, \
           current_enemy_bullet_speed, current_enemy_shoot_prob

    current_bullet_speed = BASE_BULLET_SPEED # Player bullet speed is constant
    current_enemy_speed_x = BASE_ENEMY_SPEED_X + (current_level - 1) * ENEMY_SPEED_X_INCREMENT
    current_enemy_speed_y = BASE_ENEMY_SPEED_Y
    current_enemy_bullet_speed = BASE_ENEMY_BULLET_SPEED + (current_level - 1) * ENEMY_BULLET_SPEED_INCREMENT
    current_enemy_shoot_prob = BASE_ENEMY_SHOOT_PROB + (current_level - 1) * ENEMY_SHOOT_PROB_INCREMENT
    current_enemy_shoot_prob = min(current_enemy_shoot_prob, 0.015)

def reset_game():
    """Resets all game elements to their initial state for a new game."""
    global score, lives, level, game_state, last_shot_time, \
           rapid_fire_active, rapid_fire_timer, current_player_fire_delay, \
           score_multiplier_active, score_multiplier_value, score_multiplier_timer, \
           player, high_score, player_is_dead, player_respawn_time

    # Update high score if current score is higher
    if score > high_score:
        high_score = score
        save_high_score(high_score)

    score = 0
    lives = 3
    level = 1
    game_state = "LEVEL_STARTING" # New state for wave spawn animation
    last_shot_time = pygame.time.get_ticks()

    rapid_fire_active = False
    rapid_fire_timer = 0
    current_player_fire_delay = PLAYER_FIRE_DELAY_NORMAL

    score_multiplier_active = False
    score_multiplier_value = 1
    score_multiplier_timer = 0

    player_is_dead = False
    player_respawn_time = 0

    calculate_difficulty_parameters(level)
    
    # Clear all sprite groups
    all_sprites.empty()
    player_bullets.empty()
    enemies.empty()
    enemy_bullets.empty()
import random
import sys
import os

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# --- Game Constants ---
SCREEN_WIDTH = 1800
SCREEN_HEIGHT = 900
PLAYER_SPEED = 5
PLAYER_SAFE_ZONE_HEIGHT = 600 # Player can move within the bottom 600 pixels of the screen
PLAYER_FIRE_DELAY_NORMAL = 200 # milliseconds between shots
PLAYER_FIRE_DELAY_RAPID = 100 # milliseconds for rapid fire
PLAYER_INVINCIBILITY_DURATION = 2000 # milliseconds after being hit (for flicker)
PLAYER_RESPAWN_DELAY = 1500 # milliseconds before player reappears after losing a life

# Base difficulty parameters (will increase with levels)
BASE_BULLET_SPEED = 12
BASE_ENEMY_SPEED_X = 1.0
BASE_ENEMY_SPEED_Y = 25
BASE_ENEMY_BULLET_SPEED = 6
BASE_ENEMY_SHOOT_PROB = 0.001 # Reduced initial probability for enemy to shoot
ENEMY_DESCENT_SPEED = 1.5 # Speed at which enemies fly down during spawn animation

# Difficulty scaling factors per level
ENEMY_SPEED_X_INCREMENT = 0.1
ENEMY_BULLET_SPEED_INCREMENT = 0.2
ENEMY_SHOOT_PROB_INCREMENT = 0.0002
ENEMY_ROWS_INCREMENT_PER_LEVEL = 0 # No extra rows by default, adjust if needed
MAX_ENEMY_ROWS = 10 # Cap for enemy rows

# Enemy Score Tiers (points based on row from bottom to top)
# Example: If 5 rows, points for row 0 (bottom) to row 4 (top)
ENEMY_POINTS_TIERS = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100] # Max 10 tiers for MAX_ENEMY_ROWS

# Mystery Ship (UFO) parameters
MYSTERY_SHIP_APPEAR_PROB = 0.0005 # Probability per frame for UFO to appear
MYSTERY_SHIP_SPEED = 3
MYSTERY_SHIP_POINTS = 200 # Points for shooting the UFO (increased for high value)

# Shield parameters
SHIELD_BLOCK_SIZE = 10
SHIELD_HP = 4 # How many hits a single shield block can take (more for stronger shields)

# Power-up parameters
POWERUP_DROP_PROB_ENEMY = 0.05 # 5% chance for an enemy to drop a power-up
POWERUP_DROP_PROB_UFO = 0.8 # 80% chance for UFO to drop a power-up
POWERUP_SPEED = 3
RAPID_FIRE_DURATION = 7000 # milliseconds
SCORE_MULTIPLIER_DURATION = 10000 # milliseconds
SCORE_MULTIPLIER_VALUE = 2 # e.g., 2x points

# Floating Score parameters
FLOATING_SCORE_DURATION = 1500 # milliseconds
FLOATING_SCORE_SPEED = 0.5 # pixels per frame upwards

# Starfield parameters
STAR_SPEED = 0.5 # Speed at which stars scroll downwards

# High Score file
HIGH_SCORE_FILE = "highscore.txt"

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 150, 255)
YELLOW = (255, 255, 0)
GREY = (100, 100, 100)
LIGHT_BLUE = (173, 216, 230) # For level complete message
SHIELD_COLOR = (0, 100, 0) # Dark green for shields
POWERUP_COLORS = {
    "rapid_fire": (255, 0, 255), # Magenta
    "extra_life": (0, 255, 255), # Cyan
    "score_multiplier": (255, 165, 0) # Orange
}
EXPLOSION_COLORS = [(255, 165, 0, 255), (255, 255, 0, 255)] # Orange, Yellow for explosions


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
font_huge = pygame.font.Font(None, 120)

# --- Sounds ---
player_shoot_sound = None
enemy_explosion_sound = None
player_hit_sound = None
level_up_sound = None
mystery_ship_sound = None
mystery_ship_explode_sound = None
powerup_collect_sound = None
player_explode_sound = None

try:
    script_dir = os.path.dirname(__file__)
    # Add your .wav files to the same directory as this script!
    player_shoot_sound = pygame.mixer.Sound(os.path.join(script_dir, 'laser.wav'))
    enemy_explosion_sound = pygame.mixer.Sound(os.path.join(script_dir, 'explosion.wav'))
    player_hit_sound = pygame.mixer.Sound(os.path.join(script_dir, 'hit.wav'))
    level_up_sound = pygame.mixer.Sound(os.path.join(script_dir, 'levelup.wav'))
    mystery_ship_sound = pygame.mixer.Sound(os.path.join(script_dir, 'ufo_highpitch.wav'))
    mystery_ship_explode_sound = pygame.mixer.Sound(os.path.join(script_dir, 'ufo_lowpitch.wav'))
    powerup_collect_sound = pygame.mixer.Sound(os.path.join(script_dir, 'powerup.wav'))
    player_explode_sound = pygame.mixer.Sound(os.path.join(script_dir, 'player_explode.wav'))
except (FileNotFoundError, pygame.error) as e:
    print(f"Error loading sound files: {e}. Sounds will be disabled.")

# --- Starfield background variables ---
stars = []
for _ in range(200):
    x = random.randint(0, SCREEN_WIDTH)
    y = random.randint(0, SCREEN_HEIGHT)
    size = random.randint(1, 3)
    stars.append({'x': x, 'y': y, 'size': size})

# --- High Score Load/Save ---
def load_high_score():
    """Loads the high score from a file."""
    try:
        with open(HIGH_SCORE_FILE, "r") as f:
            return int(f.read())
    except (FileNotFoundError, ValueError):
        return 0 # Return 0 if file not found or invalid content

def save_high_score(score):
    """Saves the high score to a file."""
    with open(HIGH_SCORE_FILE, "w") as f:
        f.write(str(score))

high_score = load_high_score()

# --- Classes ---

class Player(pygame.sprite.Sprite):
    """Represents the player's spaceship."""
    def __init__(self):
        super().__init__()
        self.original_image = pygame.Surface([50, 40], pygame.SRCALPHA)
        pygame.draw.polygon(self.original_image, GREEN, [(0, 40), (50, 40), (25, 0)])
        pygame.draw.rect(self.original_image, BLUE, (15, 35, 20, 10))
        self.image = self.original_image.copy() # Current image for flicker
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 30
        self.last_hit_time = 0
        self.invincible = False
        self.visible = True # For respawn flicker

    def update(self):
        # Handle movement only if visible (not during explosion/respawn)
        if self.visible:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.rect.x -= PLAYER_SPEED
            if keys[pygame.K_RIGHT]:
                self.rect.x += PLAYER_SPEED
            if keys[pygame.K_UP]:
                self.rect.y -= PLAYER_SPEED
            if keys[pygame.K_DOWN]:
                self.rect.y += PLAYER_SPEED

            # Keep player within screen bounds (X-axis)
            if self.rect.left < 0:
                self.rect.left = 0
            if self.rect.right > SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH

            # Keep player within designated safe zone (Y-axis)
            player_top_bound = SCREEN_HEIGHT - PLAYER_SAFE_ZONE_HEIGHT
            if self.rect.top < player_top_bound:
                self.rect.top = player_top_bound
            if self.rect.bottom > SCREEN_HEIGHT:
                self.rect.bottom = SCREEN_HEIGHT

        # Invincibility flicker logic
        if self.invincible:
            # Flicker effect: make sprite semi-transparent every few frames
            alpha = 255 if pygame.time.get_ticks() // 100 % 2 == 0 else 100
            self.image.set_alpha(alpha)
            if pygame.time.get_ticks() - self.last_hit_time > PLAYER_INVINCIBILITY_DURATION:
                self.invincible = False
                self.image.set_alpha(255) # Restore full opacity


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
    def __init__(self, x, y, speed_x, speed_y, initial_y_target, row_index):
        super().__init__()
        self.image = pygame.Surface([40, 30], pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, RED, (0, 0, 40, 30))
        pygame.draw.rect(self.image, GREY, (10, 10, 20, 10))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y # Start at initial y (potentially above screen)
        self.direction = 1
        self.speed_x = speed_x
        self.speed_y = speed_y # This is the "drop" speed for zig-zag
        self.initial_y_target = initial_y_target # Target Y for spawn animation
        self.spawning = True # Flag for spawn animation state
        # Assign points based on row index (from bottom up)
        self.points = ENEMY_POINTS_TIERS[min(row_index, len(ENEMY_POINTS_TIERS) - 1)]

    def update(self):
        if self.spawning:
            # Move down until it reaches its intended row position
            if self.rect.y < self.initial_y_target:
                self.rect.y += ENEMY_DESCENT_SPEED
            else:
                self.rect.y = self.initial_y_target # Snap to target
                self.spawning = False # End spawning phase
        else:
            # Normal zig-zag movement
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
        pygame.draw.ellipse(self.image, YELLOW, (0, 10, 60, 20))
        pygame.draw.ellipse(self.image, GREY, (10, 0, 40, 15))
        self.rect = self.image.get_rect()
        if random.choice([True, False]):
            self.rect.x = -self.rect.width
            self.direction = 1
        else:
            self.rect.x = SCREEN_WIDTH
            self.direction = -1
        self.rect.y = 20
        self.speed = speed

        if mystery_ship_sound:
            mystery_ship_sound.play(-1)

    def update(self):
        self.rect.x += self.speed * self.direction
        if (self.direction == 1 and self.rect.left > SCREEN_WIDTH) or \
           (self.direction == -1 and self.rect.right < 0):
            self.kill()
            if mystery_ship_sound:
                mystery_ship_sound.stop()

class ShieldBlock(pygame.sprite.Sprite):
    """Represents a single destructible block of a shield."""
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([SHIELD_BLOCK_SIZE, SHIELD_BLOCK_SIZE])
        self.image.fill(SHIELD_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.hp = SHIELD_HP

    def hit(self):
        self.hp -= 1
        if self.hp <= 0:
            self.kill()
        else:
            damage_percent = (SHIELD_HP - self.hp) / SHIELD_HP
            current_color_value = max(0, int(SHIELD_COLOR[1] * (1 - damage_percent)))
            self.image.fill((SHIELD_COLOR[0], current_color_value, SHIELD_COLOR[2]))

class PowerUp(pygame.sprite.Sprite):
    """Represents a collectible power-up."""
    def __init__(self, x, y, p_type):
        super().__init__()
        self.type = p_type
        self.image = pygame.Surface([20, 20], pygame.SRCALPHA)
        self.color = POWERUP_COLORS.get(self.type, WHITE)
        pygame.draw.circle(self.image, self.color, (10, 10), 10) # Simple circle for now
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.rect.y += POWERUP_SPEED
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    """Represents a visual explosion effect."""
    def __init__(self, center):
        super().__init__()
        self.size = 0
        self.image = pygame.Surface([60, 60], pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=center)
        self.frame = 0
        self.max_frame = 15
        self.color_fade_start = 5

    def update(self):
        self.frame += 1
        if self.frame > self.max_frame:
            self.kill()
            return

        self.image.fill((0, 0, 0, 0))
        self.size = int(30 * (self.frame / self.max_frame))

        if self.frame >= self.color_fade_start:
            alpha = max(0, 255 - int(255 * ((self.frame - self.color_fade_start) / (self.max_frame - self.color_fade_start))))
        else:
            alpha = 255

        current_color_base = random.choice(EXPLOSION_COLORS)
        current_color = (current_color_base[0], current_color_base[1], current_color_base[2], alpha)
        pygame.draw.circle(self.image, current_color, (30, 30), self.size)

class FloatingScore(pygame.sprite.Sprite):
    """Displays points earned briefly over a destroyed target."""
    def __init__(self, center, score_value):
        super().__init__()
        self.value = score_value
        self.font = font_medium
        self.color = WHITE
        self.image = self.font.render(str(self.value), True, self.color)
        self.rect = self.image.get_rect(center=center)
        self.start_time = pygame.time.get_ticks()

    def update(self):
        self.rect.y -= FLOATING_SCORE_SPEED
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time > FLOATING_SCORE_DURATION:
            self.kill()
        
        alpha = max(0, 255 - int(255 * ((current_time - self.start_time) / FLOATING_SCORE_DURATION)))
        self.image.set_alpha(alpha)


# --- Game Variables & Groups ---
all_sprites = pygame.sprite.Group()
player_bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
mystery_ships = pygame.sprite.Group()
shields = pygame.sprite.Group()
powerups = pygame.sprite.Group()
explosions = pygame.sprite.Group()
floating_scores = pygame.sprite.Group()

player = Player() # Player is now created as a global variable, but will be re-initialized by reset_game()

score = 0
lives = 3
level = 1
game_state = "MAIN_MENU" # Initial state is now MAIN_MENU
level_clear_timer = 0
last_shot_time = pygame.time.get_ticks()

# Power-up active states and timers
rapid_fire_active = False
rapid_fire_timer = 0
current_player_fire_delay = PLAYER_FIRE_DELAY_NORMAL

score_multiplier_active = False
score_multiplier_value = 1
score_multiplier_timer = 0

# Dynamic difficulty parameters (updated per level)
current_bullet_speed = BASE_BULLET_SPEED
current_enemy_speed_x = BASE_ENEMY_SPEED_X
current_enemy_speed_y = BASE_ENEMY_SPEED_Y
current_enemy_bullet_speed = BASE_ENEMY_BULLET_SPEED
current_enemy_shoot_prob = BASE_ENEMY_SHOOT_PROB

player_respawn_time = 0 # Time when player should respawn
player_is_dead = False # Flag for player death state

def calculate_difficulty_parameters(current_level):
    """Calculates game parameters based on the current level."""
    global current_bullet_speed, current_enemy_speed_x, current_enemy_speed_y, \
           current_enemy_bullet_speed, current_enemy_shoot_prob

    current_bullet_speed = BASE_BULLET_SPEED # Player bullet speed is constant
    current_enemy_speed_x = BASE_ENEMY_SPEED_X + (current_level - 1) * ENEMY_SPEED_X_INCREMENT
    current_enemy_speed_y = BASE_ENEMY_SPEED_Y
    current_enemy_bullet_speed = BASE_ENEMY_BULLET_SPEED + (current_level - 1) * ENEMY_BULLET_SPEED_INCREMENT
    current_enemy_shoot_prob = BASE_ENEMY_SHOOT_PROB + (current_level - 1) * ENEMY_SHOOT_PROB_INCREMENT
    current_enemy_shoot_prob = min(current_enemy_shoot_prob, 0.015)

def reset_game():
    """Resets all game elements to their initial state for a new game."""
    global score, lives, level, game_state, last_shot_time, \
           rapid_fire_active, rapid_fire_timer, current_player_fire_delay, \
           score_multiplier_active, score_multiplier_value, score_multiplier_timer, \
           player, high_score, player_is_dead, player_respawn_time

    # Update high score if current score is higher
    if score > high_score:
        high_score = score
        save_high_score(high_score)

    score = 0
    lives = 3
    level = 1
    game_state = "LEVEL_STARTING" # New state for wave spawn animation
    last_shot_time = pygame.time.get_ticks()

    rapid_fire_active = False
    rapid_fire_timer = 0
    current_player_fire_delay = PLAYER_FIRE_DELAY_NORMAL

    score_multiplier_active = False
    score_multiplier_value = 1
    score_multiplier_timer = 0

    player_is_dead = False
    player_respawn_time = 0

    calculate_difficulty_parameters(level)
    
    # Clear all sprite groups
    all_sprites.empty()
    player_bullets.empty()
    enemies.empty()
    enemy_bullets.empty()
    mystery_ships.empty()
    shields.empty()
    powerups.empty()
    explosions.empty()
    floating_scores.empty()

    if mystery_ship_sound: # Stop any looping UFO sound
        mystery_ship_sound.stop()

    # Re-add player and spawn new enemies/shields
    player = Player() # Create a new player object
    all_sprites.add(player)
    spawn_enemies(5, 10) # Initial enemy setup
    create_shields() # Initial shield setup

def spawn_enemies(rows, cols, x_offset=50, y_offset=50, x_padding=60, y_padding=50):
    """
    Spawns a grid of enemies with current difficulty parameters.
    Enemies start above screen and fly down to initial_y_target.
    """
    enemies.empty()
    enemy_bullets.empty()
    powerups.empty() # Clear any lingering power-ups
    floating_scores.empty() # Clear old floating scores
    # Remove these from all_sprites as well (excluding player)
    for sprite in all_sprites:
        if sprite != player and (isinstance(sprite, Enemy) or isinstance(sprite, EnemyBullet) or \
           isinstance(sprite, MysteryShip) or isinstance(sprite, PowerUp) or \
           isinstance(sprite, Explosion) or isinstance(sprite, FloatingScore)):
            sprite.kill()
    if mystery_ship_sound:
        mystery_ship_sound.stop()

    actual_rows = min(rows + (level - 1) * ENEMY_ROWS_INCREMENT_PER_LEVEL, MAX_ENEMY_ROWS)

    for row_idx in range(actual_rows): # Use row_idx for 0-based indexing
        for col in range(cols):
            # Calculate target y for this row
            target_y = y_offset + row_idx * y_padding
            # Start enemy above the screen for the spawn animation
            start_y = target_y - SCREEN_HEIGHT // 2 # Start much higher for longer descent
            
            enemy = Enemy(x_offset + col * x_padding, start_y,
                          current_enemy_speed_x, current_enemy_speed_y,
                          target_y, row_idx) # Pass target_y and row_index
            all_sprites.add(enemy)
            enemies.add(enemy)

def create_shields(num_shields=4, shield_base_y=SCREEN_HEIGHT - 100):
    """Creates a set of destructible shields."""
    shield_width = SHIELD_BLOCK_SIZE * 5
    gap_between_shields = (SCREEN_WIDTH - (num_shields * shield_width)) // (num_shields + 1)
    
    shields.empty()
    for sprite in all_sprites:
        if isinstance(sprite, ShieldBlock):
            sprite.kill()

    for i in range(num_shields):
        start_x = (i + 1) * gap_between_shields + i * shield_width
        shield_structure = [
            (0,0), (1,0), (2,0), (3,0), (4,0),
            (0,1), (1,1), (2,1), (3,1), (4,1),
            (0,2), (1,2), (3,2), (4,2),
            (0,3), (4,3)
        ]
        for dx, dy in shield_structure:
            block = ShieldBlock(start_x + dx * SHIELD_BLOCK_SIZE, shield_base_y + dy * SHIELD_BLOCK_SIZE)
            all_sprites.add(block)
            shields.add(block)

def draw_message_box(message, color, font_obj, y_offset_factor=0):
    """Draws a centered message box on the screen."""
    text_surface = font_obj.render(message, True, color)
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + y_offset_factor))

    box_padding = 20
    box_rect = text_rect.inflate(box_padding * 2, box_padding * 2)
    pygame.draw.rect(screen, BLACK, box_rect, border_radius=10)
    pygame.draw.rect(screen, color, box_rect, 3, border_radius=10)

    screen.blit(text_surface, text_rect)

def draw_lives(surface, x, y, lives_count):
    """Draws small player icons for each remaining life."""
    for i in range(lives_count):
        life_icon = pygame.Surface([25, 20], pygame.SRCALPHA)
        pygame.draw.polygon(life_icon, GREEN, [(0, 20), (25, 20), (12.5, 0)])
        surface.blit(life_icon, (x + i * 30, y))

def draw_main_menu():
    """Draws the game's main menu."""
    screen.fill(BLACK)
    # Draw scrolling stars on menu too
    for star in stars:
        pygame.draw.circle(screen, WHITE, (int(star['x']), int(star['y'])), star['size'])

    title_text = font_huge.render("SPACE INVADERS", True, WHITE)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
    screen.blit(title_text, title_rect)

    menu_options = [
        ("Start Game", "START_GAME", SCREEN_HEIGHT // 2),
        ("High Scores", "VIEW_HIGH_SCORES", SCREEN_HEIGHT // 2 + 70),
        ("Quit", "QUIT_GAME", SCREEN_HEIGHT // 2 + 140)
    ]

    for i, (text, action, y_pos) in enumerate(menu_options):
        text_surface = font_large.render(text, True, LIGHT_BLUE)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
        screen.blit(text_surface, text_rect)

    pygame.display.flip()

def draw_high_scores_screen():
    """Draws the high scores screen."""
    screen.fill(BLACK)
    for star in stars:
        pygame.draw.circle(screen, WHITE, (int(star['x']), int(star['y'])), star['size'])

    title_text = font_huge.render("HIGH SCORES", True, WHITE)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
    screen.blit(title_text, title_rect)

    score_text = font_large.render(f"1. {high_score}", True, YELLOW)
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(score_text, score_rect)

    back_text = font_medium.render("Press ESC to return to Menu", True, LIGHT_BLUE)
    back_rect = back_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
    screen.blit(back_text, back_rect)

    pygame.display.flip()


# --- Game Loop ---
running = True
while running:
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if game_state == "MAIN_MENU":
                if event.key == pygame.K_SPACE:
                    # In a full menu, you'd have selection logic
                    # For now, SPACE always starts the game directly
                    reset_game() # This will set game_state to "LEVEL_STARTING"
                elif event.key == pygame.K_h: # Simple hotkey for High Scores
                    game_state = "HIGH_SCORES_SCREEN"
                elif event.key == pygame.K_q: # Simple hotkey to Quit
                    running = False
            elif game_state == "HIGH_SCORES_SCREEN":
                if event.key == pygame.K_ESCAPE:
                    game_state = "MAIN_MENU"
            elif game_state == "RUNNING" or game_state == "LEVEL_STARTING":
                if event.key == pygame.K_SPACE:
                    # Only allow shooting if player is visible and enough time has passed
                    if player.visible and current_time - last_shot_time > current_player_fire_delay:
                        bullet = Bullet(player.rect.centerx, player.rect.top, current_bullet_speed)
                        all_sprites.add(bullet)
                        player_bullets.add(bullet)
                        if player_shoot_sound:
                            player_shoot_sound.play()
                        last_shot_time = current_time

                # Toggle pause with 'P' or 'Escape'
                if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                    game_state = "PAUSED"
            elif game_state == "PAUSED":
                if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                    game_state = "RUNNING"
            elif game_state == "GAME_OVER" or game_state == "YOU_WON":
                if event.key == pygame.K_r:
                    game_state = "MAIN_MENU" # Go back to main menu after game over/win


    # Game logic updates
    if game_state == "RUNNING":
        # Handle player death and respawn sequence
        if player_is_dead:
            if current_time - player_respawn_time > PLAYER_RESPAWN_DELAY:
                player_is_dead = False
                player.visible = True
                player.invincible = True # Player is invincible for a period after respawn
                player.last_hit_time = current_time # Reset invincibility timer
                player.rect.centerx = SCREEN_WIDTH // 2 # Reset position
                player.rect.bottom = SCREEN_HEIGHT - 30
                all_sprites.add(player) # Re-add player to sprite group
        elif player.visible: # Only update player sprite if visible
            player.update() # Update player separately
            # Update other game sprites
            for sprite in all_sprites:
                if sprite != player: # Don't update player again
                    sprite.update()

        # --- Power-up timer checks ---
        if rapid_fire_active and current_time - rapid_fire_timer > RAPID_FIRE_DURATION:
            rapid_fire_active = False
            current_player_fire_delay = PLAYER_FIRE_DELAY_NORMAL

        if score_multiplier_active and current_time - score_multiplier_timer > SCORE_MULTIPLIER_DURATION:
            score_multiplier_active = False
            score_multiplier_value = 1

        # Mystery Ship spawn logic (only if player is visible and not during spawn animation)
        if not mystery_ships and not player_is_dead and random.random() < MYSTERY_SHIP_APPEAR_PROB:
            ufo = MysteryShip(MYSTERY_SHIP_SPEED)
            all_sprites.add(ufo)
            mystery_ships.add(ufo)

        # Enemy shooting logic (only if player is visible and enemies are not spawning)
        for enemy in enemies:
            if not enemy.spawning and not player_is_dead and random.random() < current_enemy_shoot_prob:
                enemy_bullet = EnemyBullet(enemy.rect.centerx, enemy.rect.bottom, current_enemy_bullet_speed)
                all_sprites.add(enemy_bullet)
                enemy_bullets.add(enemy_bullet)

        # --- Collision Detection ---
        if not player_is_dead: # Only check player collisions if alive
            # Player Bullet-Enemy collision
            collisions = pygame.sprite.groupcollide(player_bullets, enemies, True, True)
            for bullet, enemy_list in collisions.items():
                for enemy in enemy_list:
                    points_earned = enemy.points * score_multiplier_value # Use enemy's specific points
                    score += points_earned
                    if enemy_explosion_sound:
                        enemy_explosion_sound.play()
                    
                    explosion = Explosion(enemy.rect.center)
                    all_sprites.add(explosion)
                    explosions.add(explosion)

                    floating_score = FloatingScore(enemy.rect.center, points_earned)
                    all_sprites.add(floating_score)
                    floating_scores.add(floating_score)

                    if random.random() < POWERUP_DROP_PROB_ENEMY:
                        powerup_type = random.choice(list(POWERUP_COLORS.keys()))
                        powerup = PowerUp(enemy.rect.centerx, enemy.rect.centery, powerup_type)
                        all_sprites.add(powerup)
                        powerups.add(powerup)


            # Player Bullet-Mystery Ship collision
            mystery_ship_hits = pygame.sprite.groupcollide(player_bullets, mystery_ships, True, True)
            for bullet, ufo_list in mystery_ship_hits.items():
                for ufo in ufo_list:
                    points_earned = MYSTERY_SHIP_POINTS * score_multiplier_value
                    score += points_earned
                    if mystery_ship_explode_sound:
                        mystery_ship_explode_sound.play()
                    if mystery_ship_sound:
                        mystery_ship_sound.stop()
                    
                    explosion = Explosion(ufo.rect.center)
                    all_sprites.add(explosion)
                    explosions.add(explosion)

                    floating_score = FloatingScore(ufo.rect.center, points_earned)
                    all_sprites.add(floating_score)
                    floating_scores.add(floating_score)

                    if random.random() < POWERUP_DROP_PROB_UFO:
                        powerup_type = random.choice(list(POWERUP_COLORS.keys()))
                        powerup = PowerUp(ufo.rect.centerx, ufo.rect.centery, powerup_type)
                        all_sprites.add(powerup)
                        powerups.add(powerup)


            # Enemy Bullet-Player collision
            if not player.invincible: # Only take damage if not invincible
                player_hit_by_bullet = pygame.sprite.spritecollide(player, enemy_bullets, True)
                if player_hit_by_bullet:
                    lives -= 1
                    player_is_dead = True # Player is now "dead" for a respawn sequence
                    player.visible = False # Hide player
                    player.kill() # Remove player from all_sprites temporarily
                    player_respawn_time = current_time # Start respawn timer

                    # Create explosion at player's position
                    explosion = Explosion(player.rect.center)
                    all_sprites.add(explosion)
                    explosions.add(explosion)

                    if player_hit_sound: # Sound for taking hit
                        player_hit_sound.play()
                    if player_explode_sound: # Sound for player explosion
                        player_explode_sound.play()

                    if lives <= 0:
                        game_state = "GAME_OVER"
                        if score > high_score: # Update high score on game over
                            high_score = score
                            save_high_score(high_score)

            # Player-Enemy collision (if enemies reach player or player moves into them)
            if not player.invincible: # Only take damage if not invincible
                if pygame.sprite.spritecollide(player, enemies, False):
                    lives -=1
                    player_is_dead = True
                    player.visible = False
                    player.kill()
                    player_respawn_time = current_time

                    explosion = Explosion(player.rect.center)
                    all_sprites.add(explosion)
                    explosions.add(explosion)

                    if player_hit_sound:
                        player_hit_sound.play()
                    if player_explode_sound:
                        player_explode_sound.play()

                    if lives <=0:
                        game_state = "GAME_OVER"
                        if score > high_score:
                            high_score = score
                            save_high_score(high_score)


        # Check if any enemy reached the bottom of the screen
        for enemy in enemies:
            if enemy.rect.bottom >= SCREEN_HEIGHT:
                game_state = "GAME_OVER"
                if score > high_score:
                    high_score = score
                    save_high_score(high_score)
                break

        # Check if all enemies are defeated for current level
        if not enemies:
            game_state = "LEVEL_CLEARED"
            level_clear_timer = current_time
            if level_up_sound:
                level_up_sound.play()
            if mystery_ship_sound:
                mystery_ship_sound.stop()


        # --- Shield Collisions ---
        # Player bullets hitting shields
        bullet_shield_collisions = pygame.sprite.groupcollide(player_bullets, shields, True, False)
        for bullet, shield_blocks in bullet_shield_collisions.items():
            for block in shield_blocks:
                block.hit()

        # Enemy bullets hitting shields
        enemy_bullet_shield_collisions = pygame.sprite.groupcollide(enemy_bullets, shields, True, False)
        for bullet, shield_blocks in enemy_bullet_shield_collisions.items():
            for block in shield_blocks:
                block.hit()

        # --- Player collecting Power-ups ---
        if player.visible: # Only allow collection if player is visible
            player_powerup_collisions = pygame.sprite.spritecollide(player, powerups, True)
            for powerup in player_powerup_collisions:
                if powerup_collect_sound:
                    powerup_collect_sound.play()
                if powerup.type == "rapid_fire":
                    rapid_fire_active = True
                    rapid_fire_timer = current_time
                    current_player_fire_delay = PLAYER_FIRE_DELAY_RAPID
                elif powerup.type == "extra_life":
                    lives += 1
                elif powerup.type == "score_multiplier":
                    score_multiplier_active = True
                    score_multiplier_timer = current_time
                    score_multiplier_value = SCORE_MULTIPLIER_VALUE


    elif game_state == "LEVEL_CLEARED":
        draw_message_box(f"Level {level} Complete!", LIGHT_BLUE, font_large, y_offset_factor=-50)
        draw_message_box("Preparing for next wave...", WHITE, font_medium, y_offset_factor=0)

        current_time = pygame.time.get_ticks()
        if current_time - level_clear_timer > 3000:
            level += 1
            calculate_difficulty_parameters(level)
            spawn_enemies(5, 10) # This sets enemies' initial_y_target
            create_shields() # Recreate shields for new level
            game_state = "LEVEL_STARTING" # Transition to spawn animation


    elif game_state == "LEVEL_STARTING":
        # Enemies are flying down to their positions
        all_sprites.update() # Update all sprites, including spawning enemies

        # Check if all enemies have reached their target Y positions
        all_enemies_spawned = True
        for enemy in enemies:
            if enemy.spawning:
                all_enemies_spawned = False
                break
        
        if all_enemies_spawned:
            game_state = "RUNNING" # Transition to normal gameplay


    # --- Drawing ---
    screen.fill(BLACK)

    # Draw scrolling starfield background
    for star in stars:
        star['y'] += STAR_SPEED
        if star['y'] > SCREEN_HEIGHT: # Reset star when it goes off screen
            star['y'] = 0
            star['x'] = random.randint(0, SCREEN_WIDTH) # New x for new star
        pygame.draw.circle(screen, WHITE, (int(star['x']), int(star['y'])), star['size'])


    if game_state == "MAIN_MENU":
        draw_main_menu()
    elif game_state == "HIGH_SCORES_SCREEN":
        draw_high_scores_screen()
    else: # Draw game elements for all other states (RUNNING, PAUSED, GAME_OVER, YOU_WON, LEVEL_CLEARED, LEVEL_STARTING)
        all_sprites.draw(screen) # Draws all sprites including player if visible

        # Display score, lives, and level (if not main menu or high scores)
        score_text = font_small.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        high_score_text = font_small.render(f"HIGH SCORE: {high_score}", True, WHITE)
        high_score_rect = high_score_text.get_rect(midtop=(SCREEN_WIDTH // 2, 10)) # Top center
        screen.blit(high_score_text, high_score_rect)


        level_text = font_small.render(f"Level: {level}", True, WHITE)
        level_text_rect = level_text.get_rect(midtop=(SCREEN_WIDTH // 2, high_score_rect.bottom + 5)) # Below high score
        screen.blit(level_text, level_text_rect)

        draw_lives(screen, SCREEN_WIDTH - 100, 10, lives)

        # Display power-up active indicators
        powerup_indicator_y = 40
        if rapid_fire_active:
            rf_text = font_small.render("RAPID FIRE!", True, POWERUP_COLORS["rapid_fire"])
            screen.blit(rf_text, (10, powerup_indicator_y))
            powerup_indicator_y += 20
        if score_multiplier_active:
            sm_text = font_small.render(f"SCORE x{score_multiplier_value}!", True, POWERUP_COLORS["score_multiplier"])
            screen.blit(sm_text, (10, powerup_indicator_y))


        # Display Game Over / You Won / Level Clear / Paused message
        if game_state == "GAME_OVER":
            draw_message_box("GAME OVER!", RED, font_large, y_offset_factor=-50)
            draw_message_box(f"Final Score: {score}", WHITE, font_medium, y_offset_factor=0)
            restart_text = font_medium.render("Press 'R' to return to Main Menu", True, BLUE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
            screen.blit(restart_text, restart_rect)

        elif game_state == "YOU_WON":
            draw_message_box("YOU WON!", GREEN, font_large, y_offset_factor=-50)
            draw_message_box(f"Final Score: {score}", WHITE, font_medium, y_offset_factor=0)
            restart_text = font_medium.render("Press 'R' to return to Main Menu", True, BLUE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
            screen.blit(restart_text, restart_rect)

        elif game_state == "PAUSED":
            draw_message_box("PAUSED", YELLOW, font_large, y_offset_factor=-50)
            draw_message_box("Press 'P' or 'ESC' to Resume", WHITE, font_medium, y_offset_factor=0)

    pygame.display.flip()

    clock.tick(FPS)

pygame.quit()
sys.exit()
