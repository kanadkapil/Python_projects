import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1420
SCREEN_HEIGHT = 900
PADDLE_WIDTH = 300
PADDLE_HEIGHT = 30
BALL_SIZE = 30
BRICK_WIDTH = 116
BRICK_HEIGHT = 45
ROWS = 5
COLS = 12
BULLET_WIDTH = 10
BULLET_HEIGHT = 20

# Colors
WHITE = (255, 255, 255)
BACKGROUND = (0, 0, 0)
BALL = (162, 210, 223)
PADDLE = (254, 249, 217)
POWERUP_COLORS = {
    "increase_paddle": (255, 100, 100),
    "decrease_paddle": (100, 255, 100),
    "increase_speed": (100, 100, 255),
    "multi_ball": (255, 223, 0),
    "fire_paddle": (255, 165, 0)  # New color for firing power-up
}
BRICK_COLORS = [
    (253, 139, 81),  # #FD8B51
    (242, 229, 191), # #F2E5BF
    (37, 113, 128),  # #257180
    (98, 149, 132),  # #629584
    (211, 238, 152), # #D3EE98
]

# Power-up Types
POWERUP_TYPES = ["increase_paddle", "decrease_paddle", "increase_speed", "multi_ball", "fire_paddle"]

# Screen Setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('DX Ball Game with Power-ups')

# Paddle class
class Paddle:
    def __init__(self):
        self.width = PADDLE_WIDTH
        self.rect = pygame.Rect((SCREEN_WIDTH - self.width) // 2, SCREEN_HEIGHT - PADDLE_HEIGHT - 10, self.width, PADDLE_HEIGHT)
        self.can_fire = False  # Indicates if the paddle can fire bullets
        self.bullets = []  # Store active bullets

    def move(self, dx):
        self.rect.x += dx
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.x > SCREEN_WIDTH - self.width:
            self.rect.x = SCREEN_WIDTH - self.width

    def resize(self, new_width):
        self.width = new_width
        self.rect.width = self.width

    def enable_fire(self):
        self.can_fire = True

    def shoot(self):
        if self.can_fire:
            bullet = pygame.Rect(self.rect.centerx, self.rect.y, BULLET_WIDTH, BULLET_HEIGHT)
            self.bullets.append(bullet)

    def draw(self):
        pygame.draw.rect(screen, PADDLE, self.rect)
        for bullet in self.bullets:
            pygame.draw.rect(screen, WHITE, bullet)

# Ball class
class Ball:
    def __init__(self, x=SCREEN_WIDTH // 2, y=SCREEN_HEIGHT // 2, dx=None, dy=None):
        self.rect = pygame.Rect(x, y, BALL_SIZE, BALL_SIZE)
        self.dx = dx if dx is not None else random.choice([-4, 4])
        self.dy = dy if dy is not None else -4

    def move(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

        if self.rect.x <= 0 or self.rect.x >= SCREEN_WIDTH - BALL_SIZE:
            self.dx *= -1
        if self.rect.y <= 0:
            self.dy *= -1

    def reset(self):
        self.rect.x = SCREEN_WIDTH // 2
        self.rect.y = SCREEN_HEIGHT // 2
        self.dx = random.choice([-4, 4])
        self.dy = -4

    def draw(self):
        pygame.draw.ellipse(screen, BALL, self.rect)

# Brick class
class Brick:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, BRICK_WIDTH, BRICK_HEIGHT)
        self.alive = True
        self.color = random.choice(BRICK_COLORS)

    def draw(self):
        if self.alive:
            pygame.draw.rect(screen, self.color, self.rect)

# Power-up class
class PowerUp:
    def __init__(self, x, y, type):
        self.rect = pygame.Rect(x, y, 30, 30)
        self.type = type
        self.dy = 2  # Speed of falling power-up

    def move(self):
        self.rect.y += self.dy

    def draw(self):
        pygame.draw.rect(screen, POWERUP_COLORS[self.type], self.rect)

# Main game loop
def main():
    clock = pygame.time.Clock()
    paddle = Paddle()
    ball = Ball()
    balls = [ball]
    bricks = [Brick(x * BRICK_WIDTH + 10, y * BRICK_HEIGHT + 10) for y in range(ROWS) for x in range(COLS)]
    powerups = []
    score = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            paddle.move(-10)
        if keys[pygame.K_RIGHT]:
            paddle.move(10)
        if keys[pygame.K_SPACE] and paddle.can_fire:
            paddle.shoot()

        for b in balls:
            b.move()

            # Check for collision with paddle
            if b.rect.colliderect(paddle.rect):
                b.dy *= -1
                b.rect.y = paddle.rect.y - BALL_SIZE

            # Check if ball falls below screen
            if b.rect.y > SCREEN_HEIGHT:
                balls.remove(b)
                if not balls:
                    b.reset()
                    balls.append(b)

        # Power-ups falling
        for powerup in powerups[:]:
            powerup.move()
            if powerup.rect.colliderect(paddle.rect):
                apply_powerup(powerup.type, paddle, balls)
                powerups.remove(powerup)
            elif powerup.rect.y > SCREEN_HEIGHT:
                powerups.remove(powerup)

        # Brick collisions, power-up generation, and bullet handling
        for brick in bricks:
            if brick.alive:
                # Ball collisions with bricks
                if ball.rect.colliderect(brick.rect):
                    ball.dy *= -1
                    brick.alive = False
                    score += 10
                    if random.random() < 0.2:
                        powerup_type = random.choice(POWERUP_TYPES)
                        powerups.append(PowerUp(brick.rect.x + BRICK_WIDTH // 2, brick.rect.y, powerup_type))

                # Bullet collisions with bricks
                for bullet in paddle.bullets:
                    if bullet.colliderect(brick.rect):
                        brick.alive = False
                        paddle.bullets.remove(bullet)

        # Update bullets
        for bullet in paddle.bullets[:]:
            bullet.y -= 10
            if bullet.y < 0:
                paddle.bullets.remove(bullet)

        # Draw everything
        screen.fill(BACKGROUND)
        paddle.draw()
        for b in balls:
            b.draw()
        for brick in bricks:
            brick.draw()
        for powerup in powerups:
            powerup.draw()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

def apply_powerup(type, paddle, balls):
    if type == "increase_paddle":
        paddle.resize(PADDLE_WIDTH + 100)
    elif type == "decrease_paddle":
        paddle.resize(PADDLE_WIDTH - 50)
    elif type == "increase_speed":
        for b in balls:
            b.dy *= 1.5
    elif type == "multi_ball":
        for _ in range(2):
            balls.append(Ball())
    elif type == "fire_paddle":
        paddle.enable_fire()

if __name__ == "__main__":
    main()
