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

    def __init__(self, id):
        pygame.init()
        self.squares = []
        self.turn = 1
        self.restart()
        self.id = id

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
        self.squares[knight_pos[0]][knight_pos[1]] = self.turn
        self.turn += 1
        self.squares[moves[i][0]][moves[i][1]] = 'k'

    def move_to(self, coord):
        knight_pos = self.get_knight_pos()
        self.squares[knight_pos[0]][knight_pos[1]] = self.turn
        self.turn += 1
        self.squares[coord[0]][coord[1]] = 'k'

    # Returnerar koordinaterna springaren kan flytta sig till
    def get_legit_moves(self):
        legit_moves = []
        possible_moves = [[1, 2], [-1, 2], [2, 1], [-2, 1], [2, -1], [-2, -1], [1, -2], [-1, -2]]
        knight_pos = self.get_knight_pos()
        for move in possible_moves:
            i = knight_pos[0] + move[0]
            j = knight_pos[1] + move[1]
            if self.squares[i][j] is 0:
                legit_moves.append([i, j])

        return legit_moves

    def get_knight_pos(self):
        for row in range(12):
            for column in range(12):
                if self.squares[row][column] is 'k':
                    return row, column

    # Används även för den första starten av spelet
    def restart(self):
        self.squares = self.create_board()
        i = random.randint(2, 9)
        j = random.randint(2, 9)
        self.squares[i][j] = 'k'  # placerar ut springaren på en godtycklig ruta
        self.turn = 1


class Game:
    def __init__(self):
        self.board = Board(1)
        self.screen_width = 540
        self.screen_height = 660
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.font = pygame.font.SysFont('Arial', 48)

    def draw_board(self):
        inc = self.board.INC
        self.screen.fill((0, 0, 0))
        (white, grey, black, brown) = ((225, 225, 225), (100, 100, 100), (0, 0, 0), (205, 133, 63))
        board_colors = [white, grey]

        # Draw outlining (?)
        letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        for i in range(8):
            # letters
            square = Rect((i + 1) * inc, 0, inc, inc)
            text = self.font.render(letters[i], True, black)
            text_rect = text.get_rect(center=square.center)
            pygame.draw.rect(self.screen, brown, square)
            self.screen.blit(text, text_rect)

            # numbers
            square = Rect(0, (i + 1) * inc, inc, inc)
            text = self.font.render(str(i + 1), True, black)
            text_rect = text.get_rect(center=square.center)
            pygame.draw.rect(self.screen, brown, square)
            self.screen.blit(text, text_rect)

        # Draw board squares
        c_i = 0  # color index
        for row in range(12):
            for column in range(12):
                if row not in [0, 1, 10, 11] and column not in [0, 1, 10, 11]:  # ritar inte de två yttersta raderna
                    square = Rect((column - 2 + 1) * inc, (row - 2 + 1) * inc, inc, inc)
                    pygame.draw.rect(self.screen, board_colors[c_i], square)

                    if self.board.squares[row][column] is not 0:  # Ritar ut rutans siffra om den inte är 0
                        text = self.font.render(str(self.board.squares[row][column]), True, black)
                        text_rect = text.get_rect(center=square.center)
                        self.screen.blit(text, text_rect)
                c_i = (c_i - 1) * -1  # byter mellan i=0 och i=1, vilket byter färgen på rutorna mellan vit och grå
            c_i = (c_i - 1) * -1

        # Draw buttons
        # Arguments: (x-coord, y-coord, width, height)
        buttonrandom = Rect(inc * 1, inc * 10 - (inc / 2), inc, inc)
        pygame.draw.rect(self.screen, (255, 0, 0), buttonrandom)
        buttonrandomall = Rect(inc * 2, inc * 10 - (inc / 2), inc, inc)
        pygame.draw.rect(self.screen, (0, 255, 0), buttonrandomall)
        buttonrestart = Rect(inc * 6, inc * 10 - (inc / 2), inc, inc)
        pygame.draw.rect(self.screen, (0, 0, 255), buttonrestart)
        buttonhs = Rect(inc * 7, inc * 10 - (inc / 2), inc, inc)
        pygame.draw.rect(self.screen, (255, 255, 0), buttonhs)

        # Draw score
        hs_square = Rect(inc * 3.5, inc * 10 - (inc / 2), inc * 2, inc)
        pygame.draw.rect(self.screen, (225, 225, 225), hs_square)
        text = self.font.render(str(self.board.turn), True, black)
        text_rect = text.get_rect(center=hs_square.center)
        self.screen.blit(text, text_rect)

        pygame.display.update()

    def update(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                # röd knapp
                if 60 < mouse_pos[0] < 120 and 570 < mouse_pos[1] < 630:
                    if self.board.get_legit_moves():
                        self.board.random_move()

                # grön knapp
                elif 120 < mouse_pos[0] < 180 and 570 < mouse_pos[1] < 630:
                    while self.board.get_legit_moves():
                        self.board.random_move()
                        self.draw_board()
                        time.sleep(0.05)

                # blå knapp
                elif 360 < mouse_pos[0] < 420 and 570 < mouse_pos[1] < 630:
                    save_board(self.board)
                    self.board.restart()

                elif 420 < mouse_pos[0] < 480 and 570 < mouse_pos[1] < 630:
                    self.draw_highscores()

                elif mouse_pos[1] < 540:
                    # Brädet använder omvänt än mouse_pos
                    coord = [int(mouse_pos[1] / self.board.INC) + 1, int(mouse_pos[0] / self.board.INC) + 1]
                    if coord in self.board.get_legit_moves():
                        self.board.move_to(coord)

    def draw_highscores(self):
        board_list = load_boards()
        board_list = sorted(board_list, key=lambda x: x.turn, reverse=True)

        top_five = []
        count = min(5, len(board_list))
        for i in range(count):
            top_five.append(board_list[i])

        total_turns = sum(map(lambda x: x.turn, board_list))
        count = len(board_list)
        print('Average', round(total_turns / count, 1), 'turns per game over', count, 'games.')

        showing_hs = True
        while showing_hs:
            self.screen.fill((0, 0, 0))
            top_five_rects = []
            for i, board in enumerate(top_five):
                row = Rect(0, i * 100, 540, 100)
                row_inside = Rect(5, (i * 100) + 5, 530, 90)
                pygame.draw.rect(self.screen, (0, 0, 0), row)
                pygame.draw.rect(self.screen, (222, 222, 222), row_inside)
                top_five_rects.append((row_inside, board))

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    showing_hs = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    for i in top_five_rects:
                        if i[0].collidepoint(mouse_pos[0], mouse_pos[1]):
                            self.play_board(i[1])
                            showing_hs = False

    def play_board(self, board):
        self.board = board


def main():
    game = Game()

    while True:
        game.draw_board()
        game.update()


def save_board(board):
    board_list = load_boards()
    with open('highscores.dat', 'wb') as f:
        board_list.append(board)
        pickle.dump(board_list, f)


def load_boards():
    try:
        with open('highscores.dat', 'rb') as f:
            board_list = pickle.load(f)
    except EOFError as e:
        board_list = []
        print(e)
    return board_list


if __name__ == '__main__':
    main()


