## Implemented Features

1) Singleton cards can be created with the fields name, art, qty, cost, vistory points, buying power, and action
2) Card actions include buying, playing, drawing, discarding, or destroying
3) Card actions can be required or optional
4) Cards can be uploaded via JSON template with all the same fields as the singletons
5) Cards fields can be edited
6) Cards belong to a deck that has an id that can be referenced later
7) Decks can be exported as JSON
8) Decks can be exported as PDFs
9) There is a template deck to give an example of good data
10) Games can be created out of decks
11) Number of players, starting hand size, and starting player decks can be set
12) The number of each card in the marketplace can be set
13) Whether or not the player's hand is discarded at the beginning or end of a turn can be set
14) The number of cards drawn at the beginning and end of a turn can be set
15) The number of actions (required or optional) a player's turn starts with can be set
16) Whether the end of game is triggered by number of turns passed or number of marketplace piles empty can be set
17) A game can be started
18) A player can start or end their turn
19) A player can play, buy, draw, discard, and destroy cards according to what their turn allows
20) A game ends automatically when the end of game trigger is met
21) All player scores are calculated and returned when game ends

## Future Features

1) Required actions must be done before optional ones
2) Users specify which cards cost a play
