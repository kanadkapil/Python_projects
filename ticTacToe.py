import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 300, 400  # Increased height for the message area
LINE_WIDTH = 15
BOARD_SIZE = 3
CELL_SIZE = WIDTH // BOARD_SIZE
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
FONT_COLOR = (255, 255, 255)

# Create the window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Tic Tac Toe')

# Board setup
board = [[" " for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
current_player = "X"
font = pygame.font.SysFont("Arial", 24)

def draw_board():
    screen.fill(BLACK)
    for i in range(1, BOARD_SIZE):
        pygame.draw.line(screen, WHITE, (0, CELL_SIZE * i), (WIDTH, CELL_SIZE * i), LINE_WIDTH)
        pygame.draw.line(screen, WHITE, (CELL_SIZE * i, 0), (CELL_SIZE * i, HEIGHT - 100), LINE_WIDTH)

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] == "X":
                pygame.draw.line(screen, RED, (col * CELL_SIZE + 30, row * CELL_SIZE + 30),
                                 (col * CELL_SIZE + CELL_SIZE - 30, row * CELL_SIZE + CELL_SIZE - 30), LINE_WIDTH)
                pygame.draw.line(screen, RED, (col * CELL_SIZE + CELL_SIZE - 30, row * CELL_SIZE + 30),
                                 (col * CELL_SIZE + 30, row * CELL_SIZE + CELL_SIZE - 30), LINE_WIDTH)
            elif board[row][col] == "O":
                pygame.draw.circle(screen, BLUE, (col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 2 - 30, LINE_WIDTH)

def check_winner():
    for i in range(BOARD_SIZE):
        if board[i][0] == board[i][1] == board[i][2] != " ":
            return board[i][0]
        if board[0][i] == board[1][i] == board[2][i] != " ":
            return board[0][i]
    if board[0][0] == board[1][1] == board[2][2] != " ":
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != " ":
        return board[0][2]
    return None

def is_full():
    return all(cell != " " for row in board for cell in row)

def draw_message(message):
    text = font.render(message, True, FONT_COLOR)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT - 80))

# Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouseX, mouseY = event.pos
            if mouseY < HEIGHT - 100:  # Check if click is in the board area
                row = mouseY // CELL_SIZE
                col = mouseX // CELL_SIZE
                if board[row][col] == " ":
                    board[row][col] = current_player
                    winner = check_winner()
                    if winner:
                        draw_board()
                        draw_message(f"{winner} wins!")
                        pygame.display.update()
                        pygame.time.delay(2000)
                        board = [[" " for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]  # Reset the board
                    elif is_full():
                        draw_board()
                        draw_message("It's a draw!")
                        pygame.display.update()
                        pygame.time.delay(2000)
                        board = [[" " for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]  # Reset the board
                    current_player = "O" if current_player == "X" else "X"

    draw_board()
    draw_message(f"{current_player}'s turn")
    pygame.display.update()
