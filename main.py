import random 

deck = 4 * ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", ]

random.shuffle(deck)
random.shuffle(deck)
random.shuffle(deck)
random.shuffle(deck)

def print_table():
    print("┌────┐\t\t┌────┐\t\t┌────┐\t\t┌────┐\n|    |\t\t|    |\t\t|    |\t\t|    |\n")

spades = "\u2660"

card = "┌────┐ \n|10 " + spades + "|\n|    |\n|    |\n└────┘"

print(card)

card_back = "┌────┐\n| /\ |\n| -- |\n| \/ |\n└────┘"

print(card_back)

deck_cards = "┌────┐┐\n| /\ ||\n| -- ||\n| \/ ||\n└────┘┘"

print(deck_cards)
print("\n\n")
print_table()
