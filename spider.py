#!/usr/bin/python3

#TODO: Fazer com que a tela so seja atualizada ao receber um comando valido para ver se resolve o flicker no note
#TODO: Implementar pontuacao, recolher cartas quando completar sequencia e feedback ao pressionar espaco
#      Considerar tambem nomear as colunas para facilitar a gameplay

import time
import random 
# O metodo input() nao gosta muito das setas do teclado, entao estou usando window.getch() do curses
import curses 
import os
import signal
import sys

# Funcao para tratar o SIGINT e fazer com que o programa encerre graciosamente.
def signal_handler(sig, frame):
    endwin()
    print(chr(27) + "[2J")

    if os.name == "posix": # Desesconde cursor
        os.system('tput cnorm')
    print('SIGINT/SIGTERM received, exiting now...')
    sys.exit(0)

# Registra SIGINT e associa a signal_handler.
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Linux aceita as sequencias ANSI por padrao, mas o windows precisa usar o modulo colorama
if os.name != "posix":
    from colorama import init
    init(convert=True) # Inicializa o modulo
else:
    os.system('tput civis') # Esconde cursor no linux para ficar mais bonitinho

def endwin():
    screen.erase()
    curses.nocbreak()
    curses.echo()
    screen.keypad(0)
    curses.endwin()
    return 0

# Move o cursor para uma posicao especifica.
def cursor_to(x, y): 
    print("\033[%d;%dH" % (x, y), end='')
    return 0

# Move o cursor em N linhas ou colunas para qualquer lado.
def move_cursor(direction, qtd): 
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


def set_table(deck, rows):
    for i in range(10): # Inicializa cada coluna como uma lista
        rows[i] = []

    # Distribui as cartas para cada coluna
    for i in range(0, 4):
        for j in range(0, 10):
            rows[j].append(deck.pop())

    for i in range(4):
        rows[i].append(deck.pop())

    return 0

# Funcao responsavel por imprimir a mesa com as cartas na tela. Uma bagunca mas funciona.
def print_table(rows, hidden, arrow, old_arrow):
    card_back = "┌────┐\033[1B\033[6D| /\ |\033[1B\033[6D| -- |\033[1B\033[6D| \/ |\033[1B\033[6D└────┘"

    card_placeholder = "┌────┐\033[1B\033[6D|    |\033[1B\033[6D|    |\033[1B\033[6D|    |\033[1B\033[6D└────┘"

    card_bottom = "|    |\033[1B\033[6D|    |\033[1B\033[6D└────┘"

    card_back_top = "┌────┐\033[1B\033[6D| /\ |\033[1B\033[6D"
    card_back_bottom = "| -- |\033[1B\033[6D| \/ |\033[1B\033[6D└────┘"

    x = 10
    for i in range(10):
        cursor_to(0, x)
        print("[%d]" % (i), end='')
        x += 13

    cursor_to(2, 8)

    for i in range(0,10):
        if len(rows[i]) == 0:
            print(card_placeholder, end='')
            move_cursor("up", 4)
            move_cursor("forward", 7)
        else:
            for j in range(0,len(rows[i])):
                if j < hidden[i]:
                    print(card_back_top, end='')
                    continue

                if arrow[0] == i and arrow[1] == j: # Imprime seta de selecao

                    move_cursor("backward", 2)
                    move_cursor("down", 1)

                    print("->", end='')
                    move_cursor("up", 1)

                # Apaga seta antiga.
                if old_arrow[0] == i and old_arrow[1] == j: 

                    move_cursor("backward", 2)
                    move_cursor("down", 1)
                    
                    print("  ", end='')
                    move_cursor("up", 1)

                value = rows[i][j]
                if value == '10':
                    card_top = "┌────┐\033[1B\033[6D|10 \u2660|\033[1B\033[6D"
                else:
                    card_top = "┌────┐\033[1B\033[6D|{}  \u2660|\033[1B\033[6D".format(value)
                print(card_top, end='')

            print(card_bottom, end='')
            move_cursor("up", 2 + 2 * len(rows[i]))
            move_cursor("forward", 7)

    cursor_to(0,0)
    return 0


def check_arrow(rows, arrow, direction):
    if direction == "left":
        if arrow[0] > 0:
            return True
    elif direction == "right":
        if arrow[0] < 9:
            return True
    elif direction == "up":
        if arrow[1] > 0:
            return True
    elif direction == "down":
        if arrow[1] < len(rows[arrow[0]]) - 1:
            return True


    return False

# Verifica se a proxima carta na coluna faz parte da sequencia, para que possa ser selecionada tambem caso positivo.
def check_cards(row, arrow):
    current_card = row[arrow[0]][arrow[1]]
    next_card = row[arrow[0]][arrow[1]-1]

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


def draw_cards(rows, deck, arrow):
    if len(deck) > 0:
        for i in range(10):
            rows[i].append(deck.pop())
        arrow[1] += 1

    return 0 


# Funcao responsavel por mover as cartas na mesa
def move_cards(rows, selected, num):
    current_row = rows[selected[0]]
    next_row = rows[num]

    cards = current_row[selected[1]:]

    if len(next_row) == 0 or (
            cards[0] == 'A' and next_row[-1] == '2') or (
                cards[0] == '9' and next_row[-1] == '10') or (
                    cards[0] == '10' and next_row[-1] == 'J') or (
                            cards[0] == 'J' and next_row[-1] == 'Q') or (
                                cards[0] == 'Q' and next_row[-1] == 'K') or (
                                    ord(cards[0]) == ord(next_row[-1]) - 1):

        for i in range(len(cards)):
            current_row.pop()
        # current_row = current_row[:selected[1]]
        next_row = rows[num].extend(cards)

   
# Verifica a presenca da sequencia completa em alguma das colunas
def sequence_index(row):
    sequence = ['K', 'Q', 'J', '10', '9', '8','7', '6', '5','4', '3', '2','A']

    for i in range(len(row)):
        if row[i:] == sequence:
            return i
        else:
            return -1

# Limpa a tela.
def clear_screen():
    if os.name == "posix": 
        os.system('clear') 
    else:
        os.system('cls') 

# Inicializa e configura curses
screen = curses.initscr()
curses.cbreak()
curses.noecho()
screen.timeout(-1)
screen.keypad(True)
screen.leaveok(0)


random.seed() # Inicializa o estado interno do gerador de numeros aleatorios com o tempo atual do sistema.


deck = 8 * ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"] # Cria o baralho.
rows = 10 * [None] # Cria as dez colunas.
hidden_cards = [4, 4, 4, 4, 3, 3, 3, 3, 3, 3] # Quantidade de cartas viradas para baixo em cada coluna.
arrow = [0, 4] # Posicao x e y da seta de selecao
old_arrow = [0, 0] # Coordenadas da seta na tela
check = False


# Embaralha o baralho de 5 a 8 vezes.
for i in range(random.randint(5,8)): 
    random.shuffle(deck)

# Distribui as cartass
set_table(deck, rows)
print_table(rows, hidden_cards, arrow, old_arrow)

#Loop principal.
while True:
    char = screen.getch()
    if char == ord('q') or char == 27: # q ou ESC para sair. ESC tem um delay por algum motivo
        break
    elif char == curses.KEY_LEFT:
        if check_arrow(rows, arrow, "left"):
            old_arrow = arrow.copy()
            cursor_to(20, 30)
            arrow[0] -= 1
            arrow[1] = len(rows[arrow[0]]) - 1

    elif char == curses.KEY_UP:
        if check_arrow(rows, arrow, "up"):
            if check_cards(rows, arrow) and (len(rows[arrow[0]]) - hidden_cards[arrow[0]]) > 1:
                old_arrow = arrow.copy()
                arrow[1] -= 1
    elif char == curses.KEY_RIGHT:
        if check_arrow(rows, arrow, "right"):
            old_arrow = arrow.copy()
            arrow[0] += 1
            arrow[1] = len(rows[arrow[0]]) - 1

    elif char == curses.KEY_DOWN:
        if check_arrow(rows, arrow, "down"):
            old_arrow = arrow.copy()
            arrow[1] += 1
    elif char == ord('s'):
        if len(deck) > 0:
            old_arrow = arrow.copy()
            draw_cards(rows, deck, arrow)
            check = True
    elif char == 32: # Barra de espaco
        selected = arrow.copy()

        # Permite que o getch impeça o programa de continuar executando até que seja lida input do usuario
        screen.nodelay(False)
        char = screen.getch() 
        screen.nodelay(True)

        if char >= 48 and char <= 57:
            char = char - 48
            move_cards(rows, selected, char)
            print(chr(27) + "[2J")
            arrow = [char, len(rows[char]) - 1]
            if len(rows[selected[0]]) == hidden_cards[selected[0]]:
                hidden_cards[selected[0]] -= 1

            check = True

        
    if check is True:
        #for i in range(0, 9):
            #if len(rows[i]) > 12:
                #index = sequence_index(rows[i])
                #if index > -1:
                    #rows[i] = rows[i][:index-1]

        check = False

    print_table(rows, hidden_cards, arrow, old_arrow)

endwin()

print(chr(27) + "[2J")
os.system('clear')

if os.name == "posix": # Desesconde cursor
    os.system('tput cnorm')
