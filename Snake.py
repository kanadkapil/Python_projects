import pygame
import random
import time

# Initialize pygame
pygame.init()

# Screen dimensions
screen_width = 1200
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
red = (213, 50, 80)
green = (0, 255, 0)
blue = (50, 153, 213)
yellow = (255, 215, 0)  # Color for bonus food

# Snake settings
snake_block = 20
initial_snake_speed = 15

# Font settings
font_style = pygame.font.SysFont("bahnschrift", 25)
score_font = pygame.font.SysFont("comicsansms", 25)

def display_score(score):
    value = score_font.render("Score: " + str(score), True, blue)
    screen.blit(value, [0, 0])

def draw_snake(snake_block, snake_list):
    for x in snake_list:
        pygame.draw.rect(screen, green, [x[0], x[1], snake_block, snake_block])

def game_loop():
    game_over = False
    game_close = False

    x1 = screen_width / 2
    y1 = screen_height / 2

    x1_change = 0
    y1_change = 0

    snake_list = []
    length_of_snake = 1

    # Food coordinates
    food_x = round(random.randrange(0, screen_width - snake_block) / 10.0) * 10.0
    food_y = round(random.randrange(0, screen_height - snake_block) / 10.0) * 10.0

    # Bonus food settings
    bonus_food = None
    bonus_food_timer = 0
    bonus_food_duration = 10  # seconds
    bonus_food_points = 5

    # Game settings
    score = 0
    snake_speed = initial_snake_speed
    clock = pygame.time.Clock()

    while not game_over:

        while game_close:
            screen.fill(white)
            message = font_style.render("You Lost! Press Q-Quit or C-Play Again", True, red)
            screen.blit(message, [screen_width / 6, screen_height / 3])
            display_score(score)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        game_loop()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x1_change = -snake_block
                    y1_change = 0
                elif event.key == pygame.K_RIGHT:
                    x1_change = snake_block
                    y1_change = 0
                elif event.key == pygame.K_UP:
                    y1_change = -snake_block
                    x1_change = 0
                elif event.key == pygame.K_DOWN:
                    y1_change = snake_block
                    x1_change = 0

        # Check for boundary collision
        if x1 >= screen_width or x1 < 0 or y1 >= screen_height or y1 < 0:
            game_close = True

        x1 += x1_change
        y1 += y1_change
        screen.fill(black)

        # Draw regular food
        pygame.draw.circle(screen, red, (int(food_x), int(food_y)), snake_block // 2)
        
        # Draw bonus food if active
        if bonus_food:
            pygame.draw.circle(screen, yellow, (int(bonus_food[0]), int(bonus_food[1])), snake_block // 2)
            # Check if bonus food timer has expired
            if time.time() - bonus_food_timer > bonus_food_duration:
                bonus_food = None  # Remove bonus food after timer expires

        # Snake head and body
        snake_head = [x1, y1]
        snake_list.append(snake_head)
        if len(snake_list) > length_of_snake:
            del snake_list[0]

        # Check if snake collides with itself
        for x in snake_list[:-1]:
            if x == snake_head:
                game_close = True

        draw_snake(snake_block, snake_list)
        display_score(score)

        pygame.display.update()

        # Check if snake eats regular food
        if abs(x1 - food_x) < snake_block and abs(y1 - food_y) < snake_block:
            food_x = round(random.randrange(0, screen_width - snake_block) / 10.0) * 10.0
            food_y = round(random.randrange(0, screen_height - snake_block) / 10.0) * 10.0
            length_of_snake += 1
            score += 1
            snake_speed += 1  # Gradually increase speed

            # Occasionally spawn bonus food
            if random.randint(0, 3) == 0:  # 25% chance to spawn bonus food
                bonus_food = (round(random.randrange(0, screen_width - snake_block) / 10.0) * 10.0,
                              round(random.randrange(0, screen_height - snake_block) / 10.0) * 10.0)
                bonus_food_timer = time.time()

        # Check if snake eats bonus food
        if bonus_food and abs(x1 - bonus_food[0]) < snake_block and abs(y1 - bonus_food[1]) < snake_block:
            length_of_snake += 2
            score += bonus_food_points
            bonus_food = None  # Remove bonus food after eating
            snake_speed += 2  # Boost speed for bonus food

        clock.tick(snake_speed)

    pygame.quit()
    quit()

game_loop()
