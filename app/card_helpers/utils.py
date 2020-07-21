from ..deck_helpers import utils as deck_utils


def use_action(turn, action_type):
    """
    Update current players turn having used up a single specified action
    :param turn: current player's turn
    :param action_type: type of action
    :return: None
    """
    if (turn.get(action_type)):
        required_qty = turn[action_type].get('required', 0)
        optional_qty = turn[action_type].get('optional', 0)
        # look for required qty and decrement that first
        if (required_qty > 0):
            turn[action_type]['required'] -= 1
            return
        # if no required qty, check and decrement optional
        if (optional_qty > 0):
            turn[action_type]['optional'] -= 1
            return
        # if there's infinitie allowed, just return to allow it
        if (required_qty == -1 or optional_qty == -1):
            return

    # if there wasn't any available of this action, tell the user it wasn't allowed
    raise Exception("Action not allowed")


def add_action(turn, action):
    """
    Add specified action to a turn
    :param turn: current players turn
    :param action: action to add
    :return: None
    """
    # if there isn't any of this action already in the turn, create a dictionary for it
    if (not turn.get(action['type'])):
        turn[action['type']] = dict()

    # check if the action is adding is required
    if (action['required']):
        # if there's already required actions of this type in the turn add to them, otherwise set them
        if (turn[action['type']].get('required')):
            turn[action['type']]['required'] += int(action['qty'])
        else:
            turn[action['type']]['required'] = int(action['qty'])
    # the action is adding must be option
    else:
        # if there's already option actions of this type in the turn add to them, otherwise set them
        if (turn[action['type']].get('optional')):
            turn[action['type']]['optional'] += int(action['qty'])
        else:
            turn[action['type']]['optional'] = int(action['qty'])


def equal(card1, card2):
    """
    Returns whether two cards are the same by checking their names and art
    :param card1: first card
    :param card2: second card
    :return: bool
    """
    return (card1.name == card2.name and card1.art == card2.art)


def decrement_qty(card):
    """
    Decrement the qty available of a card
    :param card: card object
    :return: card
    """
    card['qty'] = int(card['qty']) - 1
    return card


def play_card(game, args):
    """
    Update the game with the effects of playing a card
    :param game: game
    :param args: query from http request
    :return: update game
    """
    # get the current player from game and index from query args
    player = game['players'][game['curr_player']]
    index = int(args.get('index'))

    played_card = player['hand'][index]
    # get the actions from the card played (card at the index from the args in the player's hand)
    actions = played_card['actions']
    # add the actions from the card to the current player's turn
    for action in actions:
        add_action(player['current_turn'], action)
    # if the card had actions, then we use an action from the current player's turn
    if len(actions):
        use_action(player['current_turn'], 'action')

    # add the buying power from the card to the players turn
    add_action(player['current_turn'],
               {'type': 'buying_power', 'required': False, 'qty': played_card.get('buyingPower', 0)})

    # set the card in the hand as played and update the player in the game
    player['hand'][index]['played'] = True
    game['players'][game['curr_player']] = player
    return game


def buy_card(game, args):
    """
    Update the game with the effects of buying a card
    :param game: game
    :param args: query from http request
    :return: update game
    """
    marketplace = game['marketplace']
    # get the current player from game and index from query args
    player = game['players'][game['curr_player']]
    index = int(args.get('index'))

    # get card at index from request from the marketplace
    c = marketplace[index]
    # decrement amount available in the marketplace of that card
    marketplace[index] = decrement_qty(marketplace[index])
    # put the bought card into the current player's discard
    player['discard'].append(c)

    # use a buy
    use_action(player['current_turn'], 'buy')
    # use buying power equal to the cost to buy the card
    for i in range(int(c['costBuy'])):
        use_action(player['current_turn'], 'buying_power')

    # update the game's marketplace and players
    game['marketplace'] = marketplace
    game['players'][game['curr_player']] = player
    return game


def draw_cards(game, args):
    """
    Update the game with the effects of drawing a card
    :param game: game
    :param args: query from http request
    :return: update game
    """
    # get the current player from game and number to draw from query args
    player = game['players'][game['curr_player']]
    num_draw = int(args.get('num'))

    new_cards = []
    deck = player['deck']
    # draw the number of cards specified
    for i in range(num_draw):
        # use a draw action
        use_action(player['current_turn'], 'draw')
        # if no cards to draw, shuffle discard and make that the deck
        if (len(deck) == 0):
            deck = deck_utils.shuffle(player['discard'], len(player['discard']))
            player['discard'] = []
        # if cards to draw, take a card from the deck and put them in the new hand
        if (len(deck) > 0):
            new_cards.append(deck.pop())

    # set the updated hand and the player
    player['hand'] += new_cards
    game['players'][game['curr_player']] = player
    return game


def discard_card(game, args):
    """
    Update the game with the effects of discarding a card
    :param game: game
    :param args: query from http request
    :return: update game
    """
    # get the current player from game and index from query args
    player = game['players'][game['curr_player']]
    index = args.get('index')

    # use a discard action
    use_action(player['current_turn'], 'discard')

    # take the card at the specified index from the player's hand and put it into the discard (after resetting it)
    card = player['hand'].pop(int(index))
    card['played'] = False
    player['discard'].append(card)

    # update the player
    game['players'][game['curr_player']] = player
    return game


def destroy_card(game, args):
    """
    Update the game with the effects of destroying a card
    :param game: game
    :param args: query from http request
    :return: update game
    """
    # get the current player from game and index from query args
    player = game['players'][game['curr_player']]
    index = args.get('index')

    # use destroy action
    use_action(player['current_turn'], 'destroy')

    # take the card at the specified index from the player's hand and put it into the destroyed
    game['destroy'].append(player['hand'].pop(int(index)))

    # update the player
    game['players'][game['curr_player']] = player
    return game


# all the possible actions and their functions
action_functions = {
    'play': play_card,
    'buy': buy_card,
    'draw': draw_cards,
    'discard': discard_card,
    'destroy': destroy_card
}
