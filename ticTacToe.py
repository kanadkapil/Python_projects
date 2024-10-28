import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 300, 300
LINE_WIDTH = 15
BOARD_SIZE = 3
CELL_SIZE = WIDTH // BOARD_SIZE
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Create the window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Tic Tac Toe')

# Board setup
board = [[" " for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
current_player = "X"

def draw_board():
    screen.fill(WHITE)
    for i in range(1, BOARD_SIZE):
        pygame.draw.line(screen, BLACK, (0, CELL_SIZE * i), (WIDTH, CELL_SIZE * i), LINE_WIDTH)
        pygame.draw.line(screen, BLACK, (CELL_SIZE * i, 0), (CELL_SIZE * i, HEIGHT), LINE_WIDTH)

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

# Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouseX, mouseY = event.pos
            row = mouseY // CELL_SIZE
            col = mouseX // CELL_SIZE
            if board[row][col] == " ":
                board[row][col] = current_player
                winner = check_winner()
                if winner or is_full():
                    draw_board()
                    pygame.display.update()
                    pygame.time.delay(2000)
                    board = [[" " for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]  # Reset the board
                current_player = "O" if current_player == "X" else "X"
    
    draw_board()
    pygame.display.update()
