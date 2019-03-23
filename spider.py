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


def endwin(screen):
    screen.erase()
    curses.nocbreak()
    curses.echo()
    screen.keypad(0)
    curses.endwin()
    return 0

def print_time(time):
    strtime = "%02d:%02d" % (int(time/60), int(time%60))
    return strtime

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


def set_table(deck, columns):
    for i in range(10): # Inicializa cada coluna como uma lista
        columns[i] = []

    # Distribui as cartas para cada coluna
    for i in range(0, 4):
        for j in range(0, 10):
            columns[j].append(deck.pop())

    for i in range(4):
        columns[i].append(deck.pop())

    return 0

# Funcao responsavel por imprimir a mesa com as cartas na tela. Uma bagunca mas funciona.
def print_table(columns, hidden, arrow, old_arrow):
    card_back = "┌────┐\033[1B\033[6D| /\ |\033[1B\033[6D| -- |\033[1B\033[6D| \/ |\033[1B\033[6D└────┘"

    card_placeholder = "┌────┐\033[1B\033[6D|    |\033[1B\033[6D|    |\033[1B\033[6D|    |\033[1B\033[6D└────┘"

    card_bottom = "|    |\033[1B\033[6D|    |\033[1B\033[6D└────┘"

    card_back_top = "┌────┐\033[1B\033[6D| /\ |\033[1B\033[6D"
    card_back_bottom = "| -- |\033[1B\033[6D| \/ |\033[1B\033[6D└────┘"

    x = 9
    for i in range(10):
        cursor_to(0, x)
        print("[%d]" % (i), end='')
        x += 13

    cursor_to(2, 7)

    for i in range(0,10):
        if len(columns[i]) == 0:
            print(card_placeholder, end='')
            move_cursor("up", 4)
            move_cursor("forward", 7)
        else:
            for j in range(0,len(columns[i])):
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

                value = columns[i][j]
                if value == '10':
                    card_top = "┌────┐\033[1B\033[6D|10 \u2660|\033[1B\033[6D"
                else:
                    card_top = "┌────┐\033[1B\033[6D|{}  \u2660|\033[1B\033[6D".format(value)
                print(card_top, end='')

            print(card_bottom, end='')
            move_cursor("up", 2 + 2 * len(columns[i]))
            move_cursor("forward", 7)

    cursor_to(0,0)
    return 0


def check_arrow(columns, arrow, direction):
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
        if arrow[1] < len(columns[arrow[0]]) - 1:
            return True


    return False

# Verifica se a proxima carta na coluna faz parte da sequencia, para que possa ser selecionada tambem caso positivo.
def check_cards(columns, arrow):
    current_card = columns[arrow[0]][arrow[1]]
    next_card = columns[arrow[0]][arrow[1]-1]

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


def draw_cards(columns, deck, arrow):
    if len(deck) > 0:
        for i in range(10):
            columns[i].append(deck.pop())
        arrow[1] += 1

    return 0 


# Funcao responsavel por mover as cartas na mesa
def move_cards(columns, selected, num):
    current_column = columns[selected[0]]
    next_column = columns[num]
    
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


            next_column = columns[num].extend(cards)
            success = 1
    except:
        cursor_to(40, 40)
        print("Exception thrown :(")
    finally:
        return success

   
# Verifica a presenca da sequencia completa em alguma das colunas
def sequence_index(columns):
    sequence = ['K', 'Q', 'J', '10', '9', '8','7', '6', '5','4', '3', '2', 'A']

    for i in range(len(columns)):
        if columns[i:] == sequence:
            for j in range(0,13):
                columns.pop(i)
            return i
        else:
            continue

    return -1

# Limpa a tela.
def clear_screen():
    if os.name == "posix": 
        os.system('clear') 
    else:
        os.system('cls') 

    return 0
