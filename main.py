import random 
import os

if os.name != "posix": # Linux aceita as sequencias ANSI por padrao, mas o windows precisa usar a biblioteca colorama
    from colorama import init
    init(convert=True) # Permite que sequencias ANSI sejam interpretadas no Windows.


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


def print_table():
    card = "┌────┐\033[1B\033[6D|10 \u2660|\033[1B\033[6D|    |\033[1B\033[6D|    |\033[1B\033[6D└────┘"
    card_back = "┌────┐\033[1B\033[6D| /\ |\033[1B\033[6D| -- |\033[1B\033[6D| \/ |\033[1B\033[6D└────┘"
    deck_cards = "┌────┐┐\033[1B\033[7D| /\ ||\033[1B\033[7D| -- ||\033[1B\033[7D| \/ ||\033[1B\033[7D└────┘┘"
    cursor_to(5, 20)
    print(card, end='')
    move_cursor("up", 4)
    print(card_back,end='')
    move_cursor("up", 4)
    print(deck_cards, end='')

    print()

if os.name == "posix": # Limpa a tela
	os.system('clear') 
	
else:
	os.system('cls') 

random.seed() # Inicializa o estado interno do gerador de numeros aleatorios com o tempo atual do sistema.

deck = 4 * ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"] # Cria o baralho.

# Embaralha o baralho de 5 a 8 vezes.
for i in range(random.randint(5,8)): 
    random.shuffle(deck)

spades = "\u2660"

print_table()
