import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1420
SCREEN_HEIGHT = 900
PADDLE_WIDTH = 300
PADDLE_HEIGHT = 20
BALL_SIZE = 30
BRICK_WIDTH = 116
BRICK_HEIGHT = 45
ROWS = 5
COLS = 12

# Colors
WHITE = (255, 255, 255)
BACKGROUND = (0, 0, 0)
BALL = (255, 0, 0)
PADDLE = (254, 249, 217)

# Define the specified brick colors
BRICK_COLORS = [
    (253, 139, 81),  # #FD8B51
    (242, 229, 191), # #F2E5BF
    (37, 113, 128),  # #257180
    (98, 149, 132),  # #629584
    (211, 238, 152), # #D3EE98
    (100, 13, 95),   # #640D5F
    (121, 87, 87),   # #795757
    (102, 67, 67),   # #664343
    (254, 249, 217), # #FEF9D9
    (237, 62, 247),  # #ED3EF7
    (72, 207, 203)   # #48CFCB
]


# Setup screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('DX Ball Game')

# Paddle class
class Paddle:
    def __init__(self):
        self.rect = pygame.Rect((SCREEN_WIDTH - PADDLE_WIDTH) // 2, SCREEN_HEIGHT - PADDLE_HEIGHT - 10, PADDLE_WIDTH, PADDLE_HEIGHT)

    def move(self, dx):
        self.rect.x += dx
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.x > SCREEN_WIDTH - PADDLE_WIDTH:
            self.rect.x = SCREEN_WIDTH - PADDLE_WIDTH

    def draw(self):
        pygame.draw.rect(screen, PADDLE, self.rect)

# Ball class
class Ball:
    def __init__(self):
        self.rect = pygame.Rect(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, BALL_SIZE, BALL_SIZE)
        self.dx = random.choice([-4, 4])
        self.dy = -4

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
        self.color = random.choice(BRICK_COLORS)  # Assign a random color from the specified colors

    def draw(self):
        if self.alive:
            pygame.draw.rect(screen, self.color, self.rect)  # Use the assigned color

# Game Loop
def main():
    clock = pygame.time.Clock()
    paddle = Paddle()
    ball = Ball()
    bricks = [Brick(x * BRICK_WIDTH + 10, y * BRICK_HEIGHT + 10) for y in range(ROWS) for x in range(COLS)]

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

        ball.move()

        # Check for collision with paddle
        if ball.rect.colliderect(paddle.rect):
            ball.dy *= -1
            ball.rect.y = paddle.rect.y - BALL_SIZE

        # Check for collision with bricks
        for brick in bricks:
            if brick.alive and ball.rect.colliderect(brick.rect):
                ball.dy *= -1
                brick.alive = False

        # Check if ball falls below the screen
        if ball.rect.y > SCREEN_HEIGHT:
            ball.reset()

        # Clear screen
        screen.fill(BACKGROUND)

        # Draw everything
        paddle.draw()
        ball.draw()
        for brick in bricks:
            brick.draw()

        pygame.display.flip()
        clock.tick(120) #ball speed

    pygame.quit()

if __name__ == "__main__":
    main()
