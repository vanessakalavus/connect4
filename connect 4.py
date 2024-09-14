import numpy as np
import pygame
import sys
import math

# Define colors
GRAY = (192, 192, 192)  # Hall
PINK = (255, 204, 229)  # Roosa
RED = (255, 153, 153)  # Punane
YELLOW = (255, 255, 153)  # Kollane
BLACK = (0, 0, 0)  # Black for the board border
DARK_GRAY = (100, 100, 100)  # Darker gray for piece shadows

# Define new row and column counts
ROW_COUNT = 4
COLUMN_COUNT = 5

def create_board():
    board = np.zeros((ROW_COUNT, COLUMN_COUNT))
    # Set up the board with the given configuration
    board[0] = [1, 1, 2, 1, 2]  # Bottom row: red, red, yellow, red, yellow
    board[1] = [2, 1, 0, 2, 1]  # Second row: yellow, red, empty, yellow, red
    board[2] = [2, 2, 0, 2, 0]  # Third row: yellow, yellow, empty, yellow, empty
    board[3] = [1, 1, 0, 1, 0]  # Top row: red, red, empty, red, empty
    return board

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid_location(board, col):
    return board[ROW_COUNT-1][col] == 0

def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r

def print_board(board):
    print(np.flip(board, 0))

def winning_move(board, piece):
    # Check horizontal locations for win
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True

    # Check vertical locations for win
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True

    # Check positively sloped diagonals
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True

    # Check negatively sloped diagonals
    for c in range(COLUMN_COUNT-3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True

def draw_board(board):
    # Draw the board border
    pygame.draw.rect(screen, BLACK, (0, 0, width, height), 5)
    
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, GRAY, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, PINK, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            x = int(c*SQUARESIZE+SQUARESIZE/2)
            y = height - int(r*SQUARESIZE+SQUARESIZE/2)
            if board[r][c] == 1:
                pygame.draw.circle(screen, RED, (x, y), RADIUS)
                pygame.draw.circle(screen, DARK_GRAY, (x, y), RADIUS, 2)  # Add shadow effect
            elif board[r][c] == 2:
                pygame.draw.circle(screen, YELLOW, (x, y), RADIUS)
                pygame.draw.circle(screen, DARK_GRAY, (x, y), RADIUS, 2)  # Add shadow effect
    pygame.display.update()

def drop_piece_animation(col, piece):
    row = get_next_open_row(board, col)
    drop_y = -SQUARESIZE
    piece_x = int(col * SQUARESIZE + SQUARESIZE / 2)
    piece_y = -RADIUS

    while drop_y < row * SQUARESIZE:
        screen.fill(PINK)
        draw_board(board)
        piece_y += 5
        drop_y += 5
        if piece == 1:
            pygame.draw.circle(screen, RED, (piece_x, int(drop_y + SQUARESIZE / 2)), RADIUS)
        else:
            pygame.draw.circle(screen, YELLOW, (piece_x, int(drop_y + SQUARESIZE / 2)), RADIUS)
        pygame.display.update()
        pygame.time.wait(10)

    drop_piece(board, row, col, piece)

# Initialize board
board = create_board()
print_board(board)
game_over = False
turn = 0

# Initialize pygame
pygame.init()

# Define our screen size
SQUARESIZE = 100

# Define width and height of board based on the new row and column counts
width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT + 1) * SQUARESIZE

size = (width, height)
RADIUS = int(SQUARESIZE / 2 - 5)

screen = pygame.display.set_mode(size)
screen.fill(PINK)

# Draw the initial board
draw_board(board)
pygame.display.update()

# Define font for displaying win message (smaller size: 50)
myfont = pygame.font.SysFont("monospace", 50)  # Changed font size to 50

# Main game loop
while not game_over:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(screen, PINK, (0, 0, width, SQUARESIZE))
            posx = event.pos[0]
            if turn == 0:
                pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE / 2)), RADIUS)
            else:
                pygame.draw.circle(screen, YELLOW, (posx, int(SQUARESIZE / 2)), RADIUS)
        pygame.display.update()

        if event.type == pygame.MOUSEBUTTONDOWN:
            pygame.draw.rect(screen, PINK, (0, 0, width, SQUARESIZE))

            # Player 1 Turn
            if turn == 0:
                posx = event.pos[0]
                col = int(math.floor(posx / SQUARESIZE))

                if is_valid_location(board, col):
                    drop_piece_animation(col, 1)

                    if winning_move(board, 1):
                        pygame.draw.rect(screen, PINK, (0, 0, width, SQUARESIZE))  # Clear top row
                        label = myfont.render("Player 1 wins!!", 1, RED)
                        screen.blit(label, (width//2 - label.get_width()//2, 10))  # Center the win message
                        game_over = True

            # Player 2 Turn
            else:
                posx = event.pos[0]
                col = int(math.floor(posx / SQUARESIZE))

                if is_valid_location(board, col):
                    drop_piece_animation(col, 2)

                    if winning_move(board, 2):
                        pygame.draw.rect(screen, PINK, (0, 0, width, SQUARESIZE))  # Clear top row
                        label = myfont.render("Player 2 wins!!", 1, YELLOW)
                        screen.blit(label, (width//2 - label.get_width()//2, 10))  # Center the win message
                        game_over = True

            print_board(board)
            draw_board(board)

            turn += 1
            turn = turn % 2

            if game_over:
                pygame.time.wait(3000)
