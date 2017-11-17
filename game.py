from pygame.locals import *
import pygame
import sys
import time
import random
import pickle


class Board:
    width = 480
    height = 600
    INC = width / 8

    def __init__(self):
        pygame.init()
        self.board = []
        self.turn = 1
        self.restart()

    @staticmethod
    def create_board():
        _board = []
        for row in range(12):
            _board.append([])
            for column in range(12):
                if row in [0, 1, 10, 11] or column in [0, 1, 10, 11]:
                    _board[row].append(-1)
                else:
                    _board[row].append(0)

        return _board

    def random_move(self):
        moves = self.get_legit_moves()
        i = random.randint(0, len(moves) - 1)
        knight_pos = self.get_knight_pos()
        self.board[knight_pos[0]][knight_pos[1]] = self.turn
        self.turn += 1
        self.board[moves[i][0]][moves[i][1]] = 'k'

    def move_to(self, coord):
        knight_pos = self.get_knight_pos()
        self.board[knight_pos[0]][knight_pos[1]] = self.turn
        self.turn += 1
        self.board[coord[0]][coord[1]] = 'k'

    # Returnerar koordinaterna springaren kan flytta sig till
    def get_legit_moves(self):
        legit_moves = []
        possible_moves = [[1, 2], [-1, 2], [2, 1], [-2, 1], [2, -1], [-2, -1], [1, -2], [-1, -2]]
        knight_pos = self.get_knight_pos()
        for move in possible_moves:
            i = knight_pos[0] + move[0]
            j = knight_pos[1] + move[1]
            if self.board[i][j] is 0:
                legit_moves.append([i, j])

        return legit_moves

    def get_knight_pos(self):
        for row in range(12):
            for column in range(12):
                if self.board[row][column] is 'k':
                    return row, column

    # Används även för den första starten av spelet
    def restart(self):
        self.board = self.create_board()
        i = random.randint(2, 9)
        j = random.randint(2, 9)
        self.board[i][j] = 'k'  # placerar ut springaren på en godtycklig ruta
        self.turn = 1


def main():
    board = Board()
    screen_width = 540
    screen_height = 660
    screen = pygame.display.set_mode((screen_width, screen_height))
    font = pygame.font.SysFont('Arial', 48)

    while True:
        draw_board(board, screen, font)
        update(board, screen, font)

        # while board.get_legit_moves():
        #     board.random_move()
        # save_board(board)
        # board.restart()


def draw_board(board, screen, font):
    screen.fill((0, 0, 0))
    (white, grey, black, brown) = ((225, 225, 225), (100, 100, 100), (0, 0, 0), (205, 133, 63))
    board_colors = [white, grey]

    # Draw outlining (?)
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    for i in range(8):
        # letters
        square = Rect((i + 1) * board.INC, 0, board.INC, board.INC)
        text = font.render(letters[i], True, black)
        text_rect = text.get_rect(center=square.center)
        pygame.draw.rect(screen, brown, square)
        screen.blit(text, text_rect)

        # numbers
        square = Rect(0, (i + 1) * board.INC, board.INC, board.INC)
        text = font.render(str(i + 1), True, black)
        text_rect = text.get_rect(center=square.center)
        pygame.draw.rect(screen, brown, square)
        screen.blit(text, text_rect)

    # Draw board squares
    c_i = 0  # color index
    for row in range(12):
        for column in range(12):
            if row not in [0, 1, 10, 11] and column not in [0, 1, 10, 11]:  # ritar inte de två yttersta raderna
                square = Rect((column - 2 + 1) * board.INC, (row - 2 + 1) * board.INC, board.INC, board.INC)
                pygame.draw.rect(screen, board_colors[c_i], square)

                if board.board[row][column] is not 0:  # Ritar ut rutans siffra om den inte är 0
                    text = font.render(str(board.board[row][column]), True, black)
                    text_rect = text.get_rect(center=square.center)
                    screen.blit(text, text_rect)
            c_i = (c_i - 1) * -1  # byter mellan i=0 och i=1, vilket byter färgen på rutorna mellan vit och grå
        c_i = (c_i - 1) * -1

    # Draw buttons
    # Arguments: (x-coord, y-coord, width, height)
    buttonrandom = Rect(board.INC * 1, board.INC * 10 - (board.INC / 2), board.INC, board.INC)
    pygame.draw.rect(screen, (255, 0, 0), buttonrandom)
    buttonrandomall = Rect(board.INC * 2, board.INC * 10 - (board.INC / 2), board.INC, board.INC)
    pygame.draw.rect(screen, (0, 255, 0), buttonrandomall)
    buttonrestart = Rect(board.INC * 6, board.INC * 10 - (board.INC / 2), board.INC, board.INC)
    pygame.draw.rect(screen, (0, 0, 255), buttonrestart)
    buttonhs = Rect(board.INC * 7, board.INC * 10 - (board.INC / 2), board.INC, board.INC)
    pygame.draw.rect(screen, (255, 255, 0), buttonhs)

    # Draw score
    hs_square = Rect(board.INC * 3.5, board.INC * 10 - (board.INC / 2), board.INC * 2, board.INC)
    pygame.draw.rect(screen, (225, 225, 225), hs_square)
    text = font.render(str(board.turn), True, black)
    text_rect = text.get_rect(center=hs_square.center)
    screen.blit(text, text_rect)

    pygame.display.update()


# Sköter hanteringen av användarens input
def update(board, screen, font):
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            # röd knapp
            if 60 < mouse_pos[0] < 120 and 570 < mouse_pos[1] < 630:
                if board.get_legit_moves():
                    board.random_move()

            # grön knapp
            elif 120 < mouse_pos[0] < 180 and 570 < mouse_pos[1] < 630:
                while board.get_legit_moves():
                    board.random_move()
                    draw_board(board, screen, font)
                    time.sleep(0.05)

            # blå knapp
            elif 360 < mouse_pos[0] < 420 and 570 < mouse_pos[1] < 630:
                save_board(board)
                board.restart()

            elif 420 < mouse_pos[0] < 480 and 570 < mouse_pos[1] < 630:
                open_highscores()

            elif mouse_pos[1] < 540:
                # Brädet använder omvänt än mouse_pos
                coord = [int(mouse_pos[1] / board.INC) + 1, int(mouse_pos[0] / board.INC) + 1]
                if coord in board.get_legit_moves():
                    board.move_to(coord)


# hs = highscore
def open_highscores():
    board_list = load_board()
    board_list = sorted(board_list, key=lambda x: x.turn, reverse=True)
    count = min(5, len(board_list))
    for i in range(count):
        print(board_list[i].turn)

    turns = 0
    count = len(board_list)
    for i in range(count):
        turns += board_list[i].turn
    print('Average', round(turns / count, 1), 'turns per game over', count, 'games.')


def save_board(board):
    board_list = load_board()
    with open('highscores.dat', 'wb') as f:
        board_list.append(board)
        pickle.dump(board_list, f)


def load_board():
    try:
        with open('highscores.dat', 'rb') as f:
            board_list = pickle.load(f)
    except EOFError as e:
        board_list = []
        print(e)
    return board_list


if __name__ == '__main__':
    main()
