# Terminal Spider

As of today I have no plans on implementing any other game mode and/or difficulty. Currently the game only supports the 1 suit / 8 decks variant (104 cards). 

Tested on Linux with Python 3.7

## How to play

- Use the **arrow keys** to move the selection arrow on the screen. Vim keybindings are valid as well.
- Press **space** to select a card. You can move up a column to select a valid sequence instead of just the last card.
- Select the desired target column by pressing the matching key on the keyboard **[0-9]**. This works both for moving the arrow and moving cards.
- Press **'u'** to undo the last move. Each undo subtracts 10 points from the score.
- Press **'s'** to draw cards from the stock.

## Screenshots

![Example of a new game initial state](screenshots/newgame.png?raw=true)

![Quick demo of the game](screenshots/demo.gif?raw=true)

