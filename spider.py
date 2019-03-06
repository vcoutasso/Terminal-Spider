import random 
import curses # O metodo input() nao gosta muito das setas do teclado, entao estou usando window.getch() do curses
import os

if os.name != "posix": # Linux aceita as sequencias ANSI por padrao, mas o windows precisa usar o modulo colorama
    from colorama import init
    init(convert=True) # Inicializa o modulo
else:
    os.system('tput civis') # Esconde cursor no linux para ficar mais bonitinho

def cursor_to(x, y): # Move o cursor para uma posicao especifica.
    print("\033[%d;%dH" % (x, y), end='')


def move_cursor(direction, qtd): # Move o cursor em N linhas ou colunas para qualquer lado.
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
        return
        
    print("\033[%d%c" % (qtd, ch),end='') 


def set_table(deck, rows):
    for i in range(10): # Inicializa cada coluna como uma lista
        rows[i] = []

    # Distribui as cartas para cada coluna
    for i in range(0, 4):
        for j in range(0, 10):
            rows[j].append(deck.pop())

    for i in range(4):
        rows[i].append(deck.pop())

    return

# Funcao responsavel por imprimir a mesa com as cartas na tela. Uma bagunca mas funciona.
def print_table(rows, hidden, arrow):
    card_placeholder = "┌────┐\033[1B\033[6D|10 \u2660|\033[1B\033[6D|    |\033[1B\033[6D|    |\033[1B\033[6D└────┘"
    card_back = "┌────┐\033[1B\033[6D| /\ |\033[1B\033[6D| -- |\033[1B\033[6D| \/ |\033[1B\033[6D└────┘"

    card_bottom = "|    |\033[1B\033[6D|    |\033[1B\033[6D└────┘"

    card_back_top = "┌────┐\033[1B\033[6D| /\ |\033[1B\033[6D"
    card_back_bottom = "| -- |\033[1B\033[6D| \/ |\033[1B\033[6D└────┘"

    cursor_to(2, 8)

    for i in range(0,10):
        for k in range(0,hidden[i]):
            print(card_back_top, end='')

        for j in range(0,len(rows[i])-hidden[i]): 
            if arrow[0] == i and arrow[1] == j: # Imprime seta de selecao
                move_cursor("backward", 2)
                move_cursor("down", 1)
                print("->", end='')
                move_cursor("up", 1)

            value = rows[i][len(rows[i])-1-j]
            if value == '10':
                card_top = "┌────┐\033[1B\033[6D|10 \u2660|\033[1B\033[6D"
            else:
                card_top = "┌────┐\033[1B\033[6D|{}  \u2660|\033[1B\033[6D".format(value)
            print(card_top, end='')

        print(card_bottom, end='')
        move_cursor("up", 2 + 2 * len(rows[i]))
        move_cursor("forward", 6)
    

    cursor_to(60, 1)

# TODO: Implementar verificacoes para evitar que a seta seja deslocada para posicoes invalidas
def check_arrow(rows, arrow):
    return True


# Limpa a tela.
def clear_screen():
    if os.name == "posix": 
        os.system('clear') 
    else:
        os.system('cls') 


screen = curses.initscr()
curses.cbreak()
curses.noecho()
screen.timeout(10)
screen.keypad(True)

random.seed() # Inicializa o estado interno do gerador de numeros aleatorios com o tempo atual do sistema.

deck = 8 * ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"] # Cria o baralho.
rows = 10 * [None] # Cria as dez colunas.
hidden_cards = [4, 4, 4, 4, 3, 3, 3, 3, 3, 3] # Quantidade de cartas viradas para baixo em cada coluna.
arrow = [0, 0] # Posicao x e y da seta de selecao

# Embaralha o baralho de 5 a 8 vezes.
for i in range(random.randint(5,8)): 
    random.shuffle(deck)

set_table(deck, rows)

while True:
    char = screen.getch()
    print_table(rows, hidden_cards, arrow)
    if char == ord('q') or char == 27: # q ou ESC para sair. ESC tem um delay por algum motivo
        break
    elif char == curses.KEY_LEFT:
        if check_arrow(rows, arrow):
            arrow[0] -= 1
            print(chr(27) + "[2J") # Unica forma que consegui encontrar pra limpar a tela com o curses
    elif char == curses.KEY_UP:
        if check_arrow(rows, arrow):
            arrow[1] -= 1
            print(chr(27) + "[2J")
    elif char == curses.KEY_RIGHT:
        if check_arrow(rows, arrow):
            arrow[0] += 1
            print(chr(27) + "[2J")
    elif char == curses.KEY_DOWN:
        if check_arrow(rows, arrow):
            arrow[1] += 1
            print(chr(27) + "[2J")
    
screen.erase()
curses.nocbreak()
curses.echo()
screen.keypad(0)
curses.endwin()

print(chr(27) + "[2J")

if os.name == "posix": # Desesconde cursor
    os.system('tput cnorm')
