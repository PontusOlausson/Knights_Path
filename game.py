from pygame.locals import *
import pygame
import sys
import time
import random
import pickle  # modul som hanterar I/O med binary
import os

# Almänt: INC, eller inc, förekommer i koden. Denna variabel, eller konstant, är helt enkelt längden på en ruta på
# brädet. Används i metoder som lägger till saker att rita ut på skärmen, eftersom konstanten kan ses som ett (1)
# 'steg' på skärmen.
# inc = increment.


# Klass som innehåller en representation av brädet samt funktioner för att manipulera detta bräde.
class Board:
    board_width = 480
    board_height = 600
    inc = board_width / 8

    def __init__(self, _id):
        pygame.init()

        # Representerar alla rutor på brädet. Rutorna representeras av en symbol: 0 för en ruta som springaren inte
        # har passerat ännu, k för rutan som springaren befinner sig på, ett siffervärde (1, 2, 3 etc) för rutor
        # som springaren har passerat, och -1 för rutor som ligger utanför spelplanen (spelplanen består av 8x8 plus
        # två rader/kolunner som en slags 'buffer').
        self.squares = create_board_representation()

        # Brädets unika id, används för att förhindra att ett bräde sparas mer än en gång.
        self.id = _id

        self.turn = 0

        # Flagga för om brädet har en placerad springare. Används för att bestämma om spelarens nästa tryck ska placera
        # en springare eller förflytta en befintlig springare.
        self.has_placed_knight = False

    # Placerar ut springaren på angivna koordinater [x, y]
    def place_kight(self, coord):
        self.squares[coord[0]][coord[1]] = 'k'
        self.has_placed_knight = True
        self.turn += 1

    # Förflyttar springaren till en godtycklig möjlig ruta
    def random_move(self):
        moves = self.get_legit_moves()
        if moves:
            i = random.randint(0, len(moves) - 1)
            self.move_to(moves[i])

    # Förflyttar springaren till en angiven ruta [x, y]
    def move_to(self, coord):
        knight_pos = self.get_knight_pos()
        self.squares[knight_pos[0]][knight_pos[1]] = self.turn
        self.turn += 1
        self.squares[coord[0]][coord[1]] = 'k'

    # Returnerar en lista med koordinater som springaren kan flytta sig till
    def get_legit_moves(self):
        if self.has_placed_knight:
            legit_moves = []
            possible_moves = [[1, 2], [-1, 2], [2, 1], [-2, 1], [2, -1], [-2, -1], [1, -2], [-1, -2]]
            knight_pos = self.get_knight_pos()

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

        self.buttons = []
        self.initiate_buttons()

        # rgb-koder för färger som ofta används i olika metoder.
        # sparas som klassvariabler för tydlighet.
        (self.white, self.grey, self.black, self.light_grey, self.dark_grey) = \
            ((225, 225, 225), (100, 100, 100), (0, 0, 0), (200, 200, 200), (60, 60, 60))

    # Kallas när objektet först skapas. Lägger till de olika knappar som ska användas i klassvariabeln buttons[]
    def initiate_buttons(self):
        inc = self.board.inc
        self.add_button(inc / 2, inc * 10 - (inc / 2), inc, 'Next turn', self.random_move)
        self.add_button(inc / 2, inc * 11 - (inc / 2), inc, 'All turns', self.random_move_all)
        self.add_button(inc * 6, inc * 10 - (inc / 2), inc, 'Save/Restart', self.save_restart)
        self.add_button(inc * 6, inc * 11 - (inc / 2), inc, 'Highscores', self.draw_highscores)

    def add_button(self, x, y, inc, text, func):
        rect = create_rect(x, y, inc * 2.5, inc, 3)
        text = self.font_2.render(text, True, (0, 0, 0))
        text_rect = text.get_rect(center=rect.center)
        self.buttons.append([rect, text, text_rect, func])

    # Startar om spelet genom att helt enkelt skapa och tilldela ett nytt objekt för brädet
    def restart(self):
        self.board = Board(get_next_id())

    # Sparar befintligt bräde och startar sedan om spelet med ett nytt bräde.
    def save_restart(self):
        save_board(self.board)
        self.restart()

    # Kallar på brädets metod att förflytta springaren godtyckligt.
    def random_move(self):
        self.board.random_move()

    # Alternerar mellan att förflytta springaren godtyckligt och att rita ut skärmen, så länge
    # det finns en accepterbar ruta att förflytta springaren till.
    # Efter varje loop pausas programmet kort för att spelaren ska hinna se förändringar på skärmen.
    def random_move_all(self):
        while self.board.get_legit_moves():
            self.board.random_move()
            self.draw_main_screen()
            time.sleep(0.05)

    # Ritar ut
    def draw_main_screen(self):
        inc = self.board.inc  # inc = increment, används för att bestämma bredden på en ruta
        self.screen.fill(self.dark_grey)
        board_colors = [self.white, self.grey]

        # Ritar rutorna runt om själva spelplanen
        letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        for i in range(8):
            # Ritar rutorna med bokstäver
            rect = create_rect((i + 1) * inc, 0, inc, inc, 0)
            text = self.font.render(letters[i], True, self.black)
            text_rect = text.get_rect(center=rect.center)
            pygame.draw.rect(self.screen, self.light_grey, rect)
            self.screen.blit(text, text_rect)

            # Ritar rutorna med siffror
            rect = create_rect(0, (i + 1) * inc, inc, inc, 0)
            text = self.font.render(str(i + 1), True, self.black)
            text_rect = text.get_rect(center=rect.center)
            pygame.draw.rect(self.screen, self.light_grey, rect)
            self.screen.blit(text, text_rect)

        # Ritar ut brädets rutor
        c_i = 0  # color_index
        for row in range(12):
            for column in range(12):
                if row not in [0, 1, 10, 11] and column not in [0, 1, 10, 11]:  # ritar inte de två yttersta raderna
                    rect = create_rect((column - 2 + 1) * inc, (row - 2 + 1) * inc, inc, inc, 0)
                    pygame.draw.rect(self.screen, board_colors[c_i], rect)

                    if self.board.squares[row][column] is not 0:  # Ritar ut rutans siffra om den inte är 0
                        text = self.font.render(str(self.board.squares[row][column]), True, self.black)
                        text_rect = text.get_rect(center=rect.center)
                        self.screen.blit(text, text_rect)
                c_i = (c_i - 1) * -1  # byter mellan i_c=0 och i_c=1, vilket byter färgen på rutorna mellan vit och grå
            c_i = (c_i - 1) * -1

        # Ritar ut knapparna längs ned på skärmen
        # Arguments: (x-coord, y-coord, width, height)
        for button in self.buttons:
            pygame.draw.rect(self.screen, self.white, button[0])
            self.screen.blit(button[1], button[2])

        pygame.display.update()

    # Känner av om spelaren trycker på skärmen och bestämmer vilken knapp spelaren tryckte på
    def update(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                # kollar om musen är över en av knapparna, och kör i så fall knappens funktion
                for button in self.buttons:
                    if button[0].collidepoint(mouse_pos):
                        button[3]()

                # Om spelaren tryckte på en ruta på spelplanen
                if mouse_pos[1] < 540:
                    coord = [int(mouse_pos[1] / self.board.inc) + 1,
                             int(mouse_pos[0] / self.board.inc) + 1]
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
            self.screen.fill(self.dark_grey)
            top_five_rects = []
            for i, board in enumerate(top_five):
                rect = create_rect(0, i * 100, self.screen_width, 100, 5)
                pygame.draw.rect(self.screen, self.white, rect)
                top_five_rects.append((rect, board))
                text = self.font.render('Turns: ' + str(board.turn) + ', Game ID: ' + str(board.id), True, [0, 0, 0])
                text_rect = text.get_rect(center=rect.center)
                self.screen.blit(text, text_rect)

            text_str = 'Press a save to load it!'
            self.draw_text(text_str, self.screen_width / 2, self.screen_height / 12 * 9, self.white)
            text_str = 'Average ' + str(round(total_turns / max(count, 1), 1)) + \
                       ' turns per game over ' + str(count) + ' games.'
            self.draw_text(text_str, self.screen_width / 2, self.screen_height / 12 * 10, self.white)
            text_str = 'Press any button to continue.'
            self.draw_text(text_str, self.screen_width / 2, self.screen_height / 12 * 11, self.white)

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

    def draw_text(self, text, x, y, text_color):
        text = self.font_2.render(text, True, text_color)
        text_rect = text.get_rect(center=[x, y])
        self.screen.blit(text, text_rect)

    # Ersätter det befintliga brädet med ett angivet bräde, används när man laddar ett sparat bräde.
    def play_board(self, board):
        self.board = board


def create_rect(x, y, width, height, padding):
    rect = Rect(x + padding, y + padding, width - 2 * padding, height - 2 * padding)
    return rect


# Skapar och returnerar en lista som representerar rutorna på ett bräde.
def create_board_representation():
    _board = []
    for row in range(12):
        _board.append([])
        for column in range(12):
            if row in [0, 1, 10, 11] or column in [0, 1, 10, 11]:
                _board[row].append(-1)
            else:
                _board[row].append(0)

    return _board


# Används för att spara ett objekt (bräde).
# Laddar alla tidigare sparade bräden till en lista och jämnför via brädets unika id om samma bräde redan är sparat.
# Om så är fallet så skrivs det gamla sparade brädet över med det nya, annars läggs det nya till i slutet av listan.
# Till sist så sparas denna modifierade lista till filen.
# Binary.
def save_board(board):
    path = os.path.dirname(__file__) + '/highscores.dat'
    board_list = load_boards()

    if any(b.id == board.id for b in board_list):
        board_list[board.id] = board  # board.id är också brädets index i listan.
        with open(path, 'wb') as f:
            pickle.dump(board_list, f)
    else:
        board_list.append(board)
        with open(path, 'wb') as f:
            pickle.dump(board_list, f)


# Laddar och returnerar en sparad lista med objekt (bräden).
# Felhantering:
#   IOError: exempelvis om filen (highscores.dat) inte hittas.
#            Felmeddelandet skrivs ut, en ny fil (highscores.dat) skapas och en tom lista returneras.
#   EOFError: exempelvis när en tom fil (i vårat fall highscores.dat) försöker läsas.
#             Felmeddelandet skrivs ut och en tom lista returneras.
#             Detta händer när load_boards() körs innan något har sparats på filen.
def load_boards():
    path = os.path.dirname(__file__) + '/highscores.dat'
    try:
        with open(path, 'rb+') as f:
            board_list = pickle.load(f)
            return board_list
    except IOError as e:
        print(e)
        open(path, 'wb').close()
        return []
    except EOFError as e:
        print(e)
        return []


# Genererar ett nytt id för ett bräde. Returnerar det största befintliga id + 1, alternativt 0 om inga id'n existerar.
def get_next_id():
    board_list = load_boards()
    try:
        next_id = max(board.id for board in board_list) + 1
    except ValueError as e:
        print(e)
        next_id = 0
    return next_id


# Startar spelet genom att skapa ett nytt objekt av klassen Game.
def main():
    game = Game()

    # Alternerar mellan att rita ut skärmen och att kolla efter spelaraktivitet.
    while True:
        game.draw_main_screen()
        game.update()


if __name__ == '__main__':
    main()
