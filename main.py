#!/usr/bin/python3

#TODO: Implementar hints

from spider import *

# Registra SIGINT e associa a signal_handler.
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Linux aceita as sequencias ANSI por padrao, mas o windows precisa usar o modulo colorama
if os.name != "posix":
    from colorama import init
    init(convert=True) # Inicializa o modulo
else:
    os.system('tput civis') # Esconde cursor no linux para ficar mais bonitinho


start_time = time.time()

os.environ.setdefault('ESCDELAY', '25') #Diminui o delay do ESC de 1000ms para 25ms
# Inicializa e configura curses
screen = curses.initscr()
curses.cbreak()
curses.noecho()
screen.timeout(25)
screen.keypad(True)
screen.leaveok(0)


random.seed() # Inicializa o estado interno do gerador de numeros aleatorios com o tempo atual do sistema.


deck = 8 * ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"] # Cria o baralho.
columns = 10 * [None] # Cria as dez colunas.
hidden_cards = [4, 4, 4, 4, 3, 3, 3, 3, 3, 3] # Quantidade de cartas viradas para baixo em cada coluna.
arrow = [0, 4] # Posicao x e y da seta de selecao
old_arrow = [0, 0] # Coordenadas da seta na tela
check = False
sequences = 0
undo = False
score = 500
gameOver = False


# Embaralha o baralho de 5 a 8 vezes.
for i in range(random.randint(5,8)): 
    random.shuffle(deck)

# Distribui as cartas
set_table(deck, columns)

# Debugging
#columns[0] = ['1', '1', '1', '1', 'K', 'Q', 'J', '10', '9', '8', '7', '6', '5', '4', '3', '2']
#columns[1].append('A')

#Loop principal.
while True:
    char = screen.getch()

    if char == ord('q') or char == 27: # q ou ESC para sair.
        break
    elif char == curses.KEY_LEFT:
        if check_arrow(columns, arrow, "left"):
            old_arrow = arrow.copy()
            if len(columns[arrow[0] - 1]) > 0:
                arrow[0] -= 1
            elif arrow[0] > 1:
                arrow[0] -= 2
            arrow[1] = len(columns[arrow[0]]) - 1

    elif char == curses.KEY_UP:
        if check_arrow(columns, arrow, "up"):
            if check_cards(columns, arrow) and (len(columns[arrow[0]]) - hidden_cards[arrow[0]]) > 1:
                old_arrow = arrow.copy()
                arrow[1] -= 1

    elif char == curses.KEY_RIGHT:
        if check_arrow(columns, arrow, "right"):
            old_arrow = arrow.copy()
            if len(columns[arrow[0] + 1]) > 0:
                arrow[0] += 1
            elif arrow[0] < 8:
                arrow[0] += 2
            arrow[1] = len(columns[arrow[0]]) - 1

    elif char == curses.KEY_DOWN:
        if check_arrow(columns, arrow, "down"):
            old_arrow = arrow.copy()
            arrow[1] += 1

    elif char == ord('s'):
        if len(deck) > 0:
            old_arrow = arrow.copy()
            draw_cards(columns, deck, arrow)
            check = True

    elif char == 32: # Barra de espaco
        selected = arrow.copy()
        cursor_to(36, 135)
        print("\033[1;37m[Space]\033[0m")
        cursor_to(0, 0)

        # Permite que o getch impeça o programa de continuar executando até que seja lida input do usuario
        screen.nodelay(False)
        char = screen.getch() 
        screen.timeout(25)

        if char >= 48 and char <= 57:
            char = char - 48


            old_columns = [row[:] for row in columns]
            old_hidden = hidden_cards.copy()
            space_arrow = arrow.copy()
            result = move_cards(columns, selected, char)
            print(chr(27) + "[2J")
            arrow = [char, len(columns[char]) - 1]


            if len(columns[selected[0]]) == hidden_cards[selected[0]]:
                hidden_cards[selected[0]] -= 1

            if result == 1: 
                score -= 1

            undo = True
            check = True
        else:
            clear_screen()

        
    if check is True:
        for i in range(0, 9):
            if len(columns[i]) > 12:
                if sequence_index(columns[i]) != -1:
                    hidden_cards[i] -= 1
                    sequences += 1
                    score += 100
                    old_columns = [row[:] for row in columns]

        check = False

    if char == ord('u') and undo == True:
        hidden_cards = old_hidden.copy()
        columns = [row[:] for row in old_columns]
        arrow = space_arrow.copy()
        score -= 10
        undo = False
        print(chr(27) + "[2J")

    if (sequences == 8 and gameOver == False):
        cursor_to(20,65)
        print("\033[1;34mYou win! :)\033[0m")
        end_time = time.time() 
        gameOver = True


    cursor_to(2, 131)

    if score < 0:
        score = 0

    print("\033[1;37mScore: \033[1;36m{}\033[0m".format(score))
    cursor_to(4, 131)
    print("\033[1;37mSequences: \033[1;36m{}\033[0m".format(sequences))
    cursor_to(5, 131)
    print("\033[1;37mDeck: \033[1;36m{}\033[0m".format(len(deck)))
    cursor_to(7, 131)
    if gameOver == False:
        print("\033[1;37mTime: \033[1;36m{}\033[0m".format(print_time(time.time() - start_time)))
    else:
        print("\033[1;37mTime: \033[1;36m{}\033[0m".format(print_time(end_time - start_time)))
    cursor_to(0, 0)

    print_table(columns, hidden_cards, arrow, old_arrow)

endwin(screen)

print(chr(27) + "[2J")
clear_screen()

if os.name == "posix": # Desesconde cursor
    os.system('tput cnorm')
