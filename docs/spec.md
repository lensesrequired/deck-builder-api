## General Description

This project contains a Python API, deployed using Heroku, that facilitates 1) custim card designing and 2) deck building card game playing.

For the first part, the creation of a deck, the API supports a set of card attributes that the user can specify and configure. Using those, the API creates cards that the user could print and play. Users can also choose from a set of art to use as a background for a card. This is implemented using Pillow. In order to have a nice intermediate way to test the API, flask-restx will be used to supply Swagger integration and convenient modelling.

For the second part, a set of cards can be specified to be used for a game. This part takes more data from the user about the rules of the game they want to set up and will automate these rules (ie card shuffling, hand drawing, etc). To do this, a database is required. Mongo, a noSQL database, is what's used.

## Use Cases

These use cases asumes a GUI in front of the API endpoints in order to give an idea of how a user will expect the API to act.

#### GUI Deck Creator

This user lands on the web app, is shown a Create a Deck page, and is assigned a deck id in order to have persistent editing of the deck if they want to make adjustments at a later date. To start creating a deck, they add a single card by picking out a piece of provided art and inputting card details such as name, description, action, cost, point value, qty, etc.. When picking out the art, there will be a library of art to choose from. Once all the fields are entered (or as many of them as the user so chooses), they will submit the card. They can now retrieve the card's image that has the specified background art and text. If the user decides not to choose an art, the background will be all white. 

The user will continue to add cards until they have created their entire deck and along the way, users should also be able to go back and edit cards. When they are happy with their deck, they can choose to Export them to JSON that they can use to upload them easily into the editor another time or to a PDF that they can print out and cut in order to use the cards. 

#### Upload Deck Creator

This user starts out similarly to the GUI Deck Creator, but instead of creating cards one by one, they want to upload a JSON file containing all the information from their cards. They upload the file and are now able to select and edit any given card that was uploaded to make finishing touches through the same editing method as the GUI User. Just like the previous user, he can now export his deck as JSON or actual cards.

#### Game Player

This user creates a deck like either of the users above, except instead of exporting the deck, they choose to play a game with it! They are instructed to first set up the rules and gameplay. These will include things like how many players there are, what the starting hand size is, what the starting player deck consists of, what cards belong on the table to be purchased, what a turn consists of, and what the triggers are for the end of the game. Once they are submitted, a game is started!

The rest of their actions are playing out the game based on the parameters the user gave. On a players turn they will go through the sequences they specified, usually a certain number of actions (buying or playing cards), discarding their remaining cards, and redrawing their next hand. They can then end their turn and the next player will start their turn and play it through just as the first player did. 

Once the conditions for the end of a game are met (such as a certain number of turns played or so many cards bought from the market place), the end of the game is triggered and the game will display the number of victory points in every player's deck and a winner is announced. 

## Action Flows

These flows show the different actions and interactions a user will expect between themselves, a view, and this API.

<img alt="Flow Key" src="./images/flow_key.png" width="500"/>
<img alt="Game Flow" src="./images/game_flow.png" width="750"/>
<img alt="Create Flow" src="./images/create_flow.png" width="750"/>
