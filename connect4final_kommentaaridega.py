import numpy as np
import random
import pygame
import sys
import math

BLUE = (173, 216, 230)  #helesinine
GRAY = (240, 240, 240)  #helehall
YELLOW = (255, 255, 204)  #helekollane
RED = (255, 182, 193)  #heleroosa
DARK_GRAY = (100, 100, 100)  #serva värv
FONT_COLOR = (50, 50, 50)  #tumehall

ROW_COUNT = 4
COLUMN_COUNT = 5

#et eristada mängijaid
PLAYER = 0
AI = 1

EMPTY = 0
PLAYER_PIECE = 2  #mängija mängutükk on kollane
AI_PIECE = 1  #AI mängutükk on punane

WINDOW_LENGTH = 4

def create_board():
    board = np.zeros((ROW_COUNT, COLUMN_COUNT))
    board[0] = [1, 1, 2, 1, 2]
    board[1] = [2, 1, 0, 2, 1]
    board[2] = [2, 2, 0, 2, 0]
    board[3] = [1, 1, 0, 1, 0]
    return board

#mängija/ AI n-ö mängutüki õigesse kohta panemine rea ja tulba järgi
def drop_piece(board, row, col, piece): 
    board[row][col] = piece

#kontrollime kas saab valitud kohta mangutükki panna
def is_valid_location(board, col): 
    return board[ROW_COUNT - 1][col] == 0 

#leiame järgmise kasutatava/ võimaliku rea
def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r

#pöörame mängulaua vertikaalselt
def print_board(board):
    print(np.flip(board, 0))

#kontrollime kas võit on toimunud nii horisontaalselt, vertikaalselt kui ka diagonaalselt
def winning_move(board, piece):
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if all(board[r][c + i] == piece for i in range(4)):
                return True
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if all(board[r + i][c] == piece for i in range(4)):
                return True
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if all(board[r + i][c + i] == piece for i in range(4)):
                return True
    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if all(board[r - i][c + i] == piece for i in range(4)):
                return True

#skoori andmine 
def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE if piece == PLAYER_PIECE else AI_PIECE

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2
    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4

    return score

#anname skoori mingile positsioonile
def score_position(board, piece):
    score = 0
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT // 2])]
    center_count = center_array.count(piece)
    score += center_count * 3

    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLUMN_COUNT - 3):
            window = row_array[c:c + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROW_COUNT - 3):
            window = col_array[r:r + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + 3 - i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score

#kontrollime, kas AI või mängija on võitnud
def is_terminal_node(board):
    return (winning_move(board, PLAYER_PIECE) or
            winning_move(board, AI_PIECE) or
            len(get_valid_locations(board)) == 0)

#oleme siin kasutanud minmax algoritmi, et leida parim käik AI jaoks.
#alpha - max skoor maksimeerija seisukohast
#beta - min skoor minimeerija seisukohast
def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return None, 100000000000000
            elif winning_move(board, PLAYER_PIECE):
                return None, -10000000000000
            else:
                return None, 0
        else:
            return None, score_position(board, AI_PIECE)
    
    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value

    else:
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value

#funktsioon tagastab meile listi tulpadega, kuhu mängutükki on võimalik panna
def get_valid_locations(board):
    return [col for col in range(COLUMN_COUNT) if is_valid_location(board, col)]

#valib kõige parema käigu välja
def pick_best_move(board, piece):
    valid_locations = get_valid_locations(board)
    best_score = -10000
    best_col = random.choice(valid_locations)
    for col in valid_locations:
        row = get_next_open_row(board, col)
        temp_board = board.copy()
        drop_piece(temp_board, row, col, piece)
        score = score_position(temp_board, piece)
        if score > best_score:
            best_score = score
            best_col = col
    return best_col

#visualiseerime pygamei abil mängulaua detailid
def draw_board(board):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE), border_radius=15)
            pygame.draw.circle(screen, DARK_GRAY, (
                int(c * SQUARESIZE + SQUARESIZE / 2), int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)), RADIUS)

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == PLAYER_PIECE:
                pygame.draw.circle(screen, YELLOW, (
                    int(c * SQUARESIZE + SQUARESIZE / 2), height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
            elif board[r][c] == AI_PIECE:
                pygame.draw.circle(screen, RED, (
                    int(c * SQUARESIZE + SQUARESIZE / 2), height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
    pygame.display.update()

def draw_gradient():
    for i in range(height):
        color = (173 - (i // 3), 216 - (i // 5), 230 - (i // 8))  # Gradient color effect
        pygame.draw.line(screen, color, (0, i), (width, i))

#paneme mängu käima
board = create_board()
print_board(board)
game_over = False

pygame.init()

SQUARESIZE = 100
width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT + 1) * SQUARESIZE
size = (width, height)
RADIUS = int(SQUARESIZE / 2 - 5)

screen = pygame.display.set_mode(size)
pygame.display.set_caption("Connect Four")
draw_gradient()  
draw_board(board)
pygame.display.update()

myfont = pygame.font.SysFont("Arial", 75)  

turn = PLAYER

while not game_over:
    for event in pygame.event.get(): #jälgib kõiki hiireliigutusi, klikkamisi, akende kinni panemist jne
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEMOTION: #event läheb käima kui hiirt liigutatakse
            pygame.draw.rect(screen, DARK_GRAY, (0, 0, width, SQUARESIZE))
            posx = event.pos[0]
            if turn == PLAYER:
                pygame.draw.circle(screen, YELLOW, (posx, int(SQUARESIZE / 2)), RADIUS) #valitud kohale joonistatakse kollane ring

        pygame.display.update()

        if event.type == pygame.MOUSEBUTTONDOWN: #event läheb käima kui hiire nuppu vajutatakse
            pygame.draw.rect(screen, DARK_GRAY, (0, 0, width, SQUARESIZE))
            if turn == PLAYER:
                posx = event.pos[0]
                col = int(math.floor(posx / SQUARESIZE)) #teeme kindlaks millisele tulbale vajutati

                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, PLAYER_PIECE)

                    if winning_move(board, PLAYER_PIECE): #kontrollime, kas antud käik viis võiduni
                        label = myfont.render("Sina võitsid!", 1, FONT_COLOR)
                        screen.blit(label, (40, 10))
                        game_over = True
                    elif not any(is_valid_location(board, c) for c in range(COLUMN_COUNT)):
                        label = myfont.render("Viik!", 1, FONT_COLOR)
                        screen.blit(label, (40, 10))
                        game_over = True
                    
                    #siin määrame, kelle käik on (mängija = 0 ja AI = 1)
                    turn += 1
                    turn = turn % 2

                    print_board(board)
                    draw_board(board)

    if turn == AI and not game_over:
        col, minimax_score = minimax(board, 5, -math.inf, math.inf, True) #leiame AI jaoks parima käigu minmax abil

        if is_valid_location(board, col):
            row = get_next_open_row(board, col)
            drop_piece(board, row, col, AI_PIECE)

            if winning_move(board, AI_PIECE):
                label = myfont.render("AI võitis!", 1, FONT_COLOR) #siin kontrollime, kas käik viis AI võiduni
                screen.blit(label, (40, 10))
                game_over = True
            elif not any(is_valid_location(board, c) for c in range(COLUMN_COUNT)):
                label = myfont.render("Viik!", 1, FONT_COLOR)
                screen.blit(label, (40, 10))
                game_over = True

            print_board(board)
            draw_board(board)

            turn += 1
            turn = turn % 2

    if game_over:
        pygame.time.wait(3000)
        pygame.quit()           
        sys.exit()
