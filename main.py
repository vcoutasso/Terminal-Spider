import random 

deck = 4 * ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", ]

random.shuffle(deck)
random.shuffle(deck)
random.shuffle(deck)
random.shuffle(deck)

#print(deck)

spades = "\u2660"

card = "┌────┐ \n|7  " + spades + "|\n|    |\n|    |\n└────┘"

print(card)

card_back = "┌────┐\n| /\ |\n| -- |\n| \/ |\n└────┘"

print(card_back)
