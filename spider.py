#!/usr/bin/env python

import time
import random 
import curses # O metodo input() nao gosta muito das setas do teclado, entao estou usando window.getch() do curses
import os
import signal
import sys

class Spider:
    """
    Classe que representa o jogo de cartas Spider Solitaire (paciência).
    """


    def __init__(self):
        """
        Inicializa todos os atributos da classe e configura o terminal adequadamente
        """

        self.deck = 8 * ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"] # Cria o baralho.
        self.columns = 10 * [None] # Cria as dez colunas.
        self.hidden_cards = [4, 4, 4, 4, 3, 3, 3, 3, 3, 3] # Quantidade de cartas viradas para baixo em cada coluna.
        self.arrow = [0, 4] # Posicao x e y da seta de selecao
        self.old_arrow = [0, 0] # Coordenadas da seta na tela
        self.check = False
        self.sequences = 0
        self.undo = False
        self.score = 500
        self.gameOver = False

        # Embaralha o baralho de 5 a 8 vezes.
        for i in range(random.randint(5,8)):
            random.shuffle(self.deck)


    def _initial_config(self):
        """
        Método responsável por configurar o comportamento do terminal:
        Registra interrupções para não interromper o jogo de maneira abrupta e configura curses
        """
        # Registra SIGINT e associa a signal_handler.
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # Linux aceita as sequencias ANSI por padrao, mas o windows precisa usar o modulo colorama
        if os.name != "posix":
            from colorama import init
            init(convert=True) # Inicializa o modulo
        else:
            os.system('tput civis') # Esconde cursor no linux para ficar mais bonitinho

        os.environ.setdefault('ESCDELAY', '25') #Diminui o delay do ESC de 1000ms para 25ms
        # Inicializa e configura curses
        self.screen = curses.initscr()
        curses.cbreak()
        curses.noecho()
        self.screen.timeout(25)
        self.screen.keypad(True)
        self.screen.leaveok(0)

        random.seed() # Inicializa o estado interno do gerador de numeros aleatorios com o tempo atual do sistema.


    def _cleanup(self):
        """
        Limpa a saida do terminal e "devolve" o cursor para o terminal
        """

        self._endwin()

        print(chr(27) + "[2J") # Escape sequence para limpar o terminal

        if os.name == "posix": # Desesconde cursor
            os.system('tput cnorm')

        self._clear_screen()


    def _signal_handler(self, sig, frame):
        """
        Trata das interrupções recebidas e toma as ações necessárias para encerrar a execução graciosamente.
        A saída do terminal é limpa, a configuração para esconder o cursos é revertida e uma mensagem é mostrada na tela
        """

        self._cleanup()

        print('SIGINT/SIGTERM received, exiting now...')

        sys.exit(0)


    def _endwin(self):
        """
        Método responsável por encerrar o ncurses, liberando recursos e restaurando o estado do terminal antes de chamar initscr()
        """
        self.screen.erase()
        curses.nocbreak()
        curses.echo()
        self.screen.keypad(0)
        curses.endwin()
        return 0

    def _get_curr_time(self, time):
        """
        Retorna o tempo atual de jogo no formato que sera impresso na tela
        """
        strtime = "%02d:%02d" % (int(time/60), int(time%60))
        return strtime

    def _cursor_to(self, x, y):
        """
        Move o cursor para uma posicao especifica.
        """
        print("\033[%d;%dH" % (x, y), end='')
        return 0


    def _move_cursor(self, direction, qtd):
        """
        Move o cursor em N linhas ou colunas para qualquer lado.
        """
        if direction == "up":
            ch = 'A'
        elif direction == "down":
            ch = 'B'
        elif direction == "forward":
            ch = 'C'
        elif direction == "backward":
            ch = 'D'
        else:
            print("Invalid direction!")
            return 1

        print("\033[%d%c" % (qtd, ch),end='')
        return 0


    def _set_table(self):
        """
        Distribui as cartas entre todas as colunas no começo do jogo
        """
        for i in range(10): # Inicializa cada coluna como uma lista
            self.columns[i] = []

        # Distribui as cartas para cada coluna
        for i in range(0, 4):
            for j in range(0, 10):
                self.columns[j].append(self.deck.pop())

        for i in range(4):
            self.columns[i].append(self.deck.pop())

        return 0

    def _print_table(self):
        """
        Método responsável por imprimir o estado atual da mesa com todas as cartas na tela
        Números mágicos são utilizados, pois assume-se que o tamanho do terminal é padrão e o comportamento vai ser o mesmo
        """
        card_back = "┌────┐\033[1B\033[6D| /\ |\033[1B\033[6D| -- |\033[1B\033[6D| \/ |\033[1B\033[6D└────┘"

        card_placeholder = "┌────┐\033[1B\033[6D|    |\033[1B\033[6D|    |\033[1B\033[6D|    |\033[1B\033[6D└────┘"

        card_bottom = "|    |\033[1B\033[6D|    |\033[1B\033[6D└────┘"

        card_back_top = "┌────┐\033[1B\033[6D| /\ |\033[1B\033[6D"
        card_back_bottom = "| -- |\033[1B\033[6D| \/ |\033[1B\033[6D└────┘"

        hidden = self.hidden_cards

        x = 9
        for i in range(10):
            self._cursor_to(0, x)
            print("[%d]" % (i), end='')
            x += 13

        self._cursor_to(2, 7)

        for i in range(0,10):
            if len(self.columns[i]) == 0:
                print(card_placeholder, end='')
                self._move_cursor("up", 4)
                self._move_cursor("forward", 7)
            else:
                for j in range(0,len(self.columns[i])):
                    if j < hidden[i]:
                        print(card_back_top, end='')
                        continue

                    if self.arrow[0] == i and self.arrow[1] == j: # Imprime seta de selecao

                        self._move_cursor("backward", 2)
                        self._move_cursor("down", 1)

                        print("->", end='')
                        self._move_cursor("up", 1)

                    # Apaga seta antiga.
                    if self.old_arrow[0] == i and self.old_arrow[1] == j:

                        self._move_cursor("backward", 2)
                        self._move_cursor("down", 1)

                        print("  ", end='')
                        self._move_cursor("up", 1)

                    value = self.columns[i][j]
                    if value == '10':
                        card_top = "┌────┐\033[1B\033[6D|10 \u2660|\033[1B\033[6D"
                    else:
                        card_top = "┌────┐\033[1B\033[6D|{}  \u2660|\033[1B\033[6D".format(value)
                    print(card_top, end='')

                print(card_bottom, end='')
                self._move_cursor("up", 2 + 2 * len(self.columns[i]))
                self._move_cursor("forward", 7)

        self._cursor_to(0,0)
        return 0


    def _check_arrow(self, direction):
        """
        Verifica se é válido mover o cursor na posição desejada. Isso impede que o cursor vá para fora da tela e assuma posições inválidas
        """
        if direction == "left":
            if self.arrow[0] > 0:
                return True
        elif direction == "right":
            if self.arrow[0] < 9:
                return True
        elif direction == "up":
            if self.arrow[1] > 0:
                return True
        elif direction == "down":
            if self.arrow[1] < len(self.columns[self.arrow[0]]) - 1:
                return True

        return False


    def _check_cards(self):
        """
        Verifica se a proxima carta na coluna faz parte da sequencia, para que possa ser selecionada tambem caso positivo.
        """
        current_card = self.columns[self.arrow[0]][self.arrow[1]]
        next_card = self.columns[self.arrow[0]][self.arrow[1]-1]

        try:
            if int(next_card) == int(current_card) + 1:
                return True
        except ValueError:
            if current_card == '10' and next_card == 'J':
                return True
            elif current_card == 'J' and next_card == 'Q':
                return True
            elif current_card == 'Q' and next_card == 'K':
                return True
            elif current_card == 'A' and next_card == '2':
                return True

        return False


    def _draw_cards(self):
        """
        Distribui cartas do baralho entre as colunas
        """
        if len(self.deck) > 0:
            for i in range(10):
                self.columns[i].append(self.deck.pop())
            self.arrow[1] += 1

        return 0


    def _move_cards(self, selected, num):
        """
        Funcao responsavel por mover as cartas na mesa
        """
        current_column = self.columns[selected[0]]
        next_column = self.columns[num]

        success = 0

        cards = current_column[selected[1]:]
        try:
            if len(next_column) == 0 or (
                    cards[0] == 'A' and next_column[-1] == '2') or (
                        cards[0] == '9' and next_column[-1] == '10') or (
                            cards[0] == '10' and next_column[-1] == 'J') or (
                                    cards[0] == 'J' and next_column[-1] == 'Q') or (
                                        cards[0] == 'Q' and next_column[-1] == 'K') or (
                                            ord(cards[0]) == ord(next_column[-1]) - 1):

                for i in range(len(cards)):
                    current_column.pop()


                next_column = self.columns[num].extend(cards)
                success = 1
        except Exception as e:
            self._cursor_to(40, 40)
            print(f"Exception {e} thrown.")
        finally:
            return success


    def _sequence_index(self, col):
        """
        Verifica a presenca da sequencia completa em alguma das colunas
        """
        sequence = ['K', 'Q', 'J', '10', '9', '8','7', '6', '5','4', '3', '2', 'A']

        for i in range(len(col)):
            if col[i:] == sequence:
                for j in range(0,13):
                    col.pop(i)
                return i
            else:
                continue

        return -1


    def _clear_screen(self):
        """
        Limpa a tela
        """
        if os.name == "posix":
            os.system('clear')
        else:
            os.system('cls')

        return 0


    def run(self):
        """
        Método principal da classe, responsável pelo jogo em si.
        Se trata de um loop infinito que continuará executando até que o jogo se encerre
        """

        self._initial_config()
        self._set_table()
        
        # Começa a contar o tempo do jogo
        start_time = time.time()

        #Loop principal.
        while True:
            char = self.screen.getch()

            if char == ord('q') or char == 27: # q ou ESC para sair.
                break
            elif char == curses.KEY_LEFT or char == ord('h'):
                if self._check_arrow("left"):
                    self.old_arrow = self.arrow.copy()
                    if len(self.columns[self.arrow[0] - 1]) > 0:
                        self.arrow[0] -= 1
                    elif self.arrow[0] > 1:
                        self.arrow[0] -= 2
                    self.arrow[1] = len(self.columns[self.arrow[0]]) - 1

            elif char == curses.KEY_UP or char == ord('k'):
                if self._check_arrow("up"):
                    if self._check_cards() and (len(self.columns[self.arrow[0]]) - self.hidden_cards[self.arrow[0]]) > 1:
                        self.old_arrow = self.arrow.copy()
                        self.arrow[1] -= 1

            elif char == curses.KEY_RIGHT or char == ord('l'):
                if self._check_arrow("right"):
                    self.old_arrow = self.arrow.copy()
                    if len(self.columns[self.arrow[0] + 1]) > 0:
                        self.arrow[0] += 1
                    elif self.arrow[0] < 8:
                        self.arrow[0] += 2
                    self.arrow[1] = len(self.columns[self.arrow[0]]) - 1

            elif char == curses.KEY_DOWN or char == ord('j'):
                if self._check_arrow("down"):
                    self.old_arrow = self.arrow.copy()
                    self.arrow[1] += 1

            elif char == ord('s'):
                if len(self.deck) > 0:
                    self.old_arrow = self.arrow.copy()
                    self._draw_cards()
                    self.check = True

            elif char >= 48 and char <= 57:
                char = char - 48
                print(chr(27) + "[2J")
                self.arrow = [char, len(self.columns[char]) - 1]

            elif char == 32: # Barra de espaco
                selected = self.arrow.copy()
                self._cursor_to(36, 135)
                print("\033[1;37m[Space]\033[0m")
                self._cursor_to(0, 0)

                # Permite que o getch impeça o programa de continuar executando até que seja lida input do usuario
                self.screen.nodelay(False)
                char = self.screen.getch()
                self.screen.timeout(25)

                if char >= 48 and char <= 57:
                    char = char - 48


                    old_columns = [row[:] for row in self.columns]
                    old_hidden = self.hidden_cards.copy()
                    space_arrow = self.arrow.copy()
                    result = self._move_cards(selected, char)
                    print(chr(27) + "[2J")
                    self.arrow = [char, len(self.columns[char]) - 1]


                    if len(self.columns[selected[0]]) == self.hidden_cards[selected[0]]:
                        self.hidden_cards[selected[0]] -= 1

                    if result == 1:
                        self.score -= 1

                    undo = True
                    self.check = True
                else:
                    self._clear_screen()


            if self.check is True:
                for i in range(0, 9):
                    if len(self.columns[i]) > 12:
                        if self._sequence_index(self.columns[i]) != -1:
                            self.hidden_cards[i] -= 1
                            self.sequences += 1
                            self.score += 101
                            old_columns = [row[:] for row in self.columns]

                self.check = False

            if char == ord('u') and undo == True:
                self.hidden_cards = old_hidden.copy()
                self.columns = [row[:] for row in old_columns]
                arrow = space_arrow.copy()
                self.score -= 10
                undo = False
                print(chr(27) + "[2J")

            if (self.sequences == 8 and self.gameOver == False):
                self._cursor_to(20,65)
                print("\033[1;34mYou win! :)\033[0m")
                end_time = time.time()
                self.gameOver = True


            self._cursor_to(2, 131)

            if self.score < 0:
                self.score = 0

            print("\033[1;37mScore: \033[1;36m{}\033[0m".format(self.score))
            self._cursor_to(4, 131)
            print("\033[1;37mSequences: \033[1;36m{}\033[0m".format(self.sequences))
            self._cursor_to(5, 131)
            print("\033[1;37mDeck: \033[1;36m{}\033[0m".format(len(self.deck)))
            self._cursor_to(7, 131)
            if self.gameOver == False:
                print("\033[1;37mTime: \033[1;36m{}\033[0m".format(self._get_curr_time(time.time() - start_time)))
            else:
                print("\033[1;37mTime: \033[1;36m{}\033[0m".format(self._get_curr_time(end_time - start_time)))

            self._cursor_to(0, 0)

            self._print_table()

        self._cleanup()


if __name__ == "__main__":
    game = Spider()
    game.run()
