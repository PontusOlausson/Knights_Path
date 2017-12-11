from pygame.locals import *
import pygame
import sys
import time
import random
import pickle
import os


# Klass som innehåller en representation av brädet samt funktioner för att manipulera detta bräde.
class Board:
    board_width = 480
    board_height = 600
    square_width = board_width / 8

    def __init__(self, _id):
        pygame.init()

        # Representerar alla rutor på spelplanen. Rutorna representeras av en symbol: 0 för en ruta som springaren inte
        # har passerat ännu, k för rutan som springaren befinner sig på, ett siffervärde (1, 2, 3 etc) för rutor
        # som springaren har passerat, och -1 för rutor som ligger utanför spelplanen (spelplanen består av 8x8 plus
        # två rader/kolunner som en slags 'buffer').
        self.squares = self.create_board()
        self.turn = 1

        # Brädets unika id, används för att förhindra att ett bräde sparas mer än en gång.
        self.id = _id

        self.turn = 0

        # Flagga för om brädet har en placerad springare. Används för att bestämma om spelarens nästa tryck ska placera
        # en springare eller förflytta en befintlig springare.
        self.has_placed_knight = False

    # Placerar ut springaren på koordinater (x, y)
    def place_kight(self, coord):
        self.squares[coord[0]][coord[1]] = 'k'
        self.has_placed_knight = True
        self.turn += 1

    # Placerar ut springaren på en godtycklig ruta
    def place_knight_random(self):
        i = random.randint(2, 9)
        j = random.randint(2, 9)
        self.place_kight([i, j])

    # Skapar och returnerar en representation av ett tomt bräde.
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

    # Förflyttar springaren till en godtycklig möjlig ruta
    def random_move(self):
        moves = self.get_legit_moves()
        i = random.randint(0, len(moves) - 1)
        self.move_to(moves[i])

    # Förflyttar springaren till en angiven ruta
    def move_to(self, coord):
        knight_pos = self.get_knight_pos()
        self.squares[knight_pos[0]][knight_pos[1]] = self.turn
        self.turn += 1
        self.squares[coord[0]][coord[1]] = 'k'

    # Returnerar en lista med koordinater som springaren kan flytta sig till
    def get_legit_moves(self):
        legit_moves = []
        possible_moves = [[1, 2], [-1, 2], [2, 1], [-2, 1], [2, -1], [-2, -1], [1, -2], [-1, -2]]
        knight_pos = self.get_knight_pos()

        if knight_pos:
            for move in possible_moves:
                i = knight_pos[0] + move[0]
                j = knight_pos[1] + move[1]
                if self.squares[i][j] is 0:
                    legit_moves.append([i, j])

            return legit_moves

    # Returnerar koordinaterna som springaren befinner sig på
    def get_knight_pos(self):
        for row in range(12):
            for column in range(12):
                if self.squares[row][column] is 'k':
                    return row, column


# En klass som innehåller variabler och funktioner som rör själva spelet.
class Game:
    def __init__(self):
        # Skapar ett nytt objekt som representerar brädet.
        self.board = Board(get_next_id())

        # Variabler och konstanter som rör den grafiska visningen av spelet.
        self.screen_width = 540
        self.screen_height = 730
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.font = pygame.font.SysFont('Arial', 48)
        self.font_2 = pygame.font.SysFont('Arial', 32)

        light_grey, black = (225, 225, 225), (0, 0, 0)
        inc = self.board.square_width
        self.buttons = []
        self.add_button(inc / 2, inc * 10 - (inc / 2), inc, 'Next turn', black)
        self.add_button(inc / 2, inc * 11 - (inc / 2), inc, 'All turns', black)
        self.add_button(inc * 6, inc * 10 - (inc / 2), inc, 'Save/Restart', black)
        self.add_button(inc * 6, inc * 11 - (inc / 2), inc, 'Highscores', black)

    # Startar om spelet genom att helt enkelt skapa och tilldela ett nytt objekt för brädet
    def restart(self):
        self.board = Board(get_next_id())

    # Ritar ut
    def draw_main_screen(self):
        inc = self.board.square_width  # inc = increment, används för att bestämma bredden på en ruta
        self.screen.fill((60, 60, 60))
        (white, grey, black, light_grey) = ((225, 225, 225), (100, 100, 100), (0, 0, 0), (200, 200, 200))
        board_colors = [white, grey]

        # Ritar rutorna runt om själva spelplanen
        letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        for i in range(8):
            # Ritar rutorna med bokstäver
            square = Rect((i + 1) * inc, 0, inc, inc)
            text = self.font.render(letters[i], True, black)
            text_rect = text.get_rect(center=square.center)
            pygame.draw.rect(self.screen, light_grey, square)
            self.screen.blit(text, text_rect)

            # Ritar rutorna med siffror
            square = Rect(0, (i + 1) * inc, inc, inc)
            text = self.font.render(str(i + 1), True, black)
            text_rect = text.get_rect(center=square.center)
            pygame.draw.rect(self.screen, light_grey, square)
            self.screen.blit(text, text_rect)

        # Ritar ut brädets rutor
        c_i = 0  # color_index
        for row in range(12):
            for column in range(12):
                if row not in [0, 1, 10, 11] and column not in [0, 1, 10, 11]:  # ritar inte de två yttersta raderna
                    square = Rect((column - 2 + 1) * inc, (row - 2 + 1) * inc, inc, inc)
                    pygame.draw.rect(self.screen, board_colors[c_i], square)

                    if self.board.squares[row][column] is not 0:  # Ritar ut rutans siffra om den inte är 0
                        text = self.font.render(str(self.board.squares[row][column]), True, black)
                        text_rect = text.get_rect(center=square.center)
                        self.screen.blit(text, text_rect)
                c_i = (c_i - 1) * -1  # byter mellan i_c=0 och i_c=1, vilket byter färgen på rutorna mellan vit och grå
            c_i = (c_i - 1) * -1

        # Ritar ut knapparna längs ned på skärmen
        # Arguments: (x-coord, y-coord, width, height)
        for button in self.buttons:
            pygame.draw.rect(self.screen, (225, 225, 225), button[0])
            self.screen.blit(button[1], button[2])

        # Ritar ut poängen mellan knapparna
        hs_square = Rect(inc * 3.5, inc * 10 - (inc / 2), inc * 2, inc)
        pygame.draw.rect(self.screen, (225, 225, 225), hs_square)
        text = self.font.render(str(self.board.turn), True, black)
        text_rect = text.get_rect(center=hs_square.center)
        self.screen.blit(text, text_rect)

        pygame.display.update()

    def add_button(self, x, y, inc, text, text_color):
        button = Rect(x + 3, y + 3, inc * 2.5 - 6, inc - 6)
        text = self.font_2.render(text, True, text_color)
        text_rect = text.get_rect(center=button.center)
        self.buttons.append([button, text, text_rect])

    # Känner av om spelaren trycker på skärmen och bestämmer vilken knapp spelaren tryckte på
    def update(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                # Next turn: förflyttar springaren godtyckligt
                if self.buttons[0][0].collidepoint(mouse_pos):
                    if self.board.get_legit_moves():
                        self.board.random_move()

                # All turns: förflyttar springaren godtyckligt tills dess att springare inte längre kan förflytta sig.
                elif self.buttons[1][0].collidepoint(mouse_pos):
                    while self.board.get_legit_moves():
                        self.board.random_move()
                        self.draw_main_screen()
                        time.sleep(0.05)

                # Save/Restart: sparar och startar om spelet
                elif self.buttons[2][0].collidepoint(mouse_pos):
                    save_board(self.board)
                    self.restart()

                # Highscores: öppnar poängsidan
                elif self.buttons[3][0].collidepoint(mouse_pos):
                    self.draw_highscores()

                # Om spelaren tryckte på en ruta på spelplanen
                elif mouse_pos[1] < 540:
                    coord = [int(mouse_pos[1] / self.board.square_width) + 1,
                             int(mouse_pos[0] / self.board.square_width) + 1]
                    if not self.board.has_placed_knight:
                        self.board.place_kight(coord)
                    else:
                        # Brädet använder omvänt än mouse_pos
                        if coord in self.board.get_legit_moves():
                            self.board.move_to(coord)

    def draw_highscores(self):
        # Laddar alla sparade bräden och sorterar dessa med avseende på 'poäng'
        board_list = load_boards()
        board_list = sorted(board_list, key=lambda x: x.turn, reverse=True)

        top_five = []
        count = min(5, len(board_list))
        for i in range(count):
            top_five.append(board_list[i])

        # Totala 'poäng' i alla sparade bräden
        total_turns = sum(map(lambda x: x.turn, board_list))
        count = len(board_list)

        # Ritar upp poängsidan tills dess att spelaren trycker på en knapp eller laddar ett sparat bräde.
        showing_hs = True
        while showing_hs:
            self.screen.fill((60, 60, 60))
            top_five_rects = []
            for i, board in enumerate(top_five):
                rect = Rect(0, i * 100, 540, 100)
                inside_rect = Rect(5, (i * 100) + 5, 530, 90)
                pygame.draw.rect(self.screen, (60, 60, 60), rect)
                pygame.draw.rect(self.screen, (222, 222, 222), inside_rect)
                top_five_rects.append((inside_rect, board))
                text = self.font.render('Turns: ' + str(board.turn) + ', Game ID: ' + str(board.id), True, [0, 0, 0])
                text_rect = text.get_rect(center=inside_rect.center)
                self.screen.blit(text, text_rect)

            text_str = 'Average ' + str(round(total_turns / max(count, 1), 1)) + \
                       ' turns per game over ' + str(count) + ' games.'
            text = self.font_2.render(text_str, True, [255, 255, 255])
            text_rect = text.get_rect(center=(self.screen_width / 2, self.screen_height / 12 * 10))
            self.screen.blit(text, text_rect)
            text_str = 'Press any button to continue.'
            text = self.font_2.render(text_str, True, [255, 255, 255])
            text_rect = text.get_rect(center=(self.screen_width / 2, self.screen_height / 12 * 11))
            self.screen.blit(text, text_rect)

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

    # Ersätter det befintliga brädet med ett angivet bräde, används när man laddar ett sparat bräde.
    def play_board(self, board):
        self.board = board


def save_board(board):
    path = os.path.dirname(__file__) + '/highscores.dat'
    board_list = load_boards()
    if not any(b.id == board.id for b in board_list):
        with open(path, 'wb') as f:
            board_list.append(board)
            pickle.dump(board_list, f)


def load_boards():
    path = os.path.dirname(__file__) + '/highscores.dat'
    try:
        with open(path, 'rb+') as f:
            board_list = pickle.load(f)
    except IOError as e:
        print(e)
        open(path, 'wb').close()
        board_list = []
    except EOFError as e:
        print(e)
        board_list = []
    return board_list


def get_next_id():
    board_list = load_boards()
    try:
        next_id = max(board.id for board in board_list) + 1
    except ValueError as e:
        print(e)
        next_id = 0
    return next_id


def main():
    game = Game()

    while True:
        game.draw_main_screen()
        game.update()


if __name__ == '__main__':
    main()
