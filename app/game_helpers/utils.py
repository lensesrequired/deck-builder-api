from ..deck_helpers import utils as deck_utils


def setup_player(index, settings):
    """
    Creates a player based on the user specified settings
    :param index: int
    :param settings: settings hash
    :return: player hash
    """
    # default player
    player = {
        'name': 'Player ' + str(index + 1),
        'discard': [],
        'deck': [],
        'hand': [],
        'current_turn': None
    }

    # for each card in the starting deck,
    # add individuals of that card for the correct quantity as specified in the settings
    # then shuffle it and set it as the players deck
    starting_deck = [card for card in settings['starting_deck'] for i in range(int(card['qty']))]
    player['deck'] = deck_utils.shuffle(starting_deck, len(player['deck']))

    # grab the user specified starting hand size off the deck and set that as the player's hand
    hand = []
    for i in range(settings['starting_hand_size']):
        hand.append(player['deck'].pop())
    player['hand'] = hand

    return player


def start_turn(player, settings):
    """
    Update a player into the started turn state by setting it's current_turn
    :param player: player who's turn should be started
    :param settings: player specified settings
    :return: player
    """
    # check settings for draws and discards
    actions = settings['turn']['pre']
    discard = int(actions.get('discard', dict()).get('required', 0)) == -1
    draw = int(actions.get('draw', dict()).get('required', 0))

    # discard cards
    if (discard == -1):
        for card in player['hand']:
            card['played'] = False
            player['discard'].append(card)
        player['hand'] = []

    # draw new cards
    new_cards = []
    deck = player['deck']
    for i in range(draw):
        # if players deck runs out, shuffle discard and make that the players deck
        if (len(deck) == 0):
            deck = deck_utils.shuffle(player['discard'], len(player['discard']))
            player['discard'] = []

        # pop card off deck and put it into the new hand (as long as there's card to be had)
        if (len(deck) > 0):
            new_cards.append(deck.pop())
    player['deck'] = deck
    player['hand'] += new_cards

    # set player's current turn with the actions from the user specified turn
    player['current_turn'] = settings['turn']['during']
    # set the initial buying power for a turn to 0
    player['current_turn']['buying_power'] = {'optional': 0}
    return player


def end_turn(player, settings):
    """
    Update a player into the ended turn state by setting it's current_turn and doing post turn actions
    :param player: player who's turn should be ended
    :return: player
    """
    player['current_turn'] = None

    # check settings for draws and discards
    actions = settings['turn']['post']
    discard = int(actions.get('discard', dict()).get('required', 0)) == -1
    draw = int(actions.get('draw', dict()).get('required', 0))

    # discard cards
    if (discard == -1):
        for card in player['hand']:
            card['played'] = False
            player['discard'].append(card)
        player['hand'] = []

    # draw new cards
    new_cards = []
    deck = player['deck']
    for i in range(draw):
        # if players deck runs out, shuffle discard and make that the players deck
        if (len(deck) == 0):
            deck = deck_utils.shuffle(player['discard'], len(player['discard']))
            player['discard'] = []

        # pop card off deck and put it into the new hand (as long as there's card to be had)
        if (len(deck) > 0):
            new_cards.append(deck.pop())
    player['deck'] = deck
    player['hand'] += new_cards

    return player


def check_end_triggers(end_trigger, num_turns, marketplace):
    """
    Based on the end of game trigger, return whether or not the game is over
    :param end_trigger: object containing attributes type and qty
    :param num_turns: number
    :param marketplace: list of cards
    :return: boolean
    """
    trigger_type = end_trigger.get('type', '')
    trigger_qty = int(end_trigger.get('qty', 0))

    # if the trigger type is turns,
    # return whether there's been at least the set number of turns played
    if (trigger_type == 'turns'):
        return int(num_turns) >= trigger_qty
    # if the trigger type is piles,
    # return whether there's been at least that many piles emptied in the marketplace
    elif (trigger_type == 'piles'):
        # create a list of the cards with qty 0
        empty_piles = [card for card in marketplace if int(card.get('qty', 0)) == 0]
        return len(empty_piles) >= trigger_qty


def check_turn_actions(player):
    """
    Returns how many required actions there are left in a player's turn
    :param player: current player
    :return: int
    """
    curr_turn = player['current_turn']

    # if there's no cards to draw don't check for required draws
    if (len(player['deck'] + player['discard']) == 0):
        if (curr_turn.get('draw')):
            del curr_turn['draw']

    # if there's no cards to play don't worry about required plays, discards, or destroys
    playable_cards = [card for card in player['hand'] if (not card.get('played', False))]
    if (len(playable_cards) == 0):
        if (curr_turn.get('discard')):
            del curr_turn['discard']
        if (curr_turn.get('destroy')):
            del curr_turn['destroy']
        if (curr_turn.get('play')):
            del curr_turn['play']

    # sum up all the required actions left (and if there's infinite of one available, give it a positive value)
    return sum([
        int(curr_turn[action_type].get('required', 0) or 0)
        if int(curr_turn[action_type].get('required', 0) or 0) > -1
        else 1
        for action_type in list(curr_turn)])


def calculate_stats(game):
    """
    Calculate and return the total points for each player and the winner of the game
    :param game: game object
    :return: object contain winner and dictionary of player scores
    """
    stats = {
        'player_points': dict(),
        'winner': ('', -1)
    }

    for player in game['players']:
        all_cards = player['hand'] + player['discard'] + player['deck']

        # add up the victory points of all the cards in the player's possession
        points = sum([int(card['victoryPoints']) for card in all_cards])
        stats['player_points'][player['name']] = points

        # if they have more points than the current winner, set them as the new winner
        if (points > stats['winner'][1]):
            stats['winner'] = (player['name'], points)
    return stats
