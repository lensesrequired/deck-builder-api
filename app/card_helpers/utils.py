from ..deck_helpers import utils as deck_utils


def use_action(turn, action_type):
    # look for required and decrement that first
    if (turn.get(action_type)):
        if (turn[action_type].get('required')):
            turn[action_type]['required'] -= 1
            return
        if (turn[action_type].get('optional')):
            turn[action_type]['optional'] -= 1
            return
    turn[action_type] = {'optional': -1}


def add_action(turn, action):
    if (not turn.get(action['type'])):
        turn[action['type']] = dict()
    if (action['required']):
        if (not turn[action['type']].get('required')):
            turn[action['type']]['required'] = int(action['qty'])
        else:
            turn[action['type']]['required'] += int(action['qty'])
    else:
        if (not turn[action['type']].get('optional')):
            turn[action['type']]['optional'] = int(action['qty'])
        else:
            turn[action['type']]['optional'] += int(action['qty'])


def equal(card1, card2):
    return (card1.name == card2.name and card1.art == card2.art)


def decrement_qty(card):
    card['qty'] = int(card['qty']) - 1
    return card


def play_card(game, args):
    player = game['players'][game['curr_player']]
    index = int(args.get('index'))
    actions = player['hand'][index]['actions']
    for action in actions:
        add_action(player['current_turn'], action)
    if len(actions):
        use_action(player['current_turn'], 'action')
    player['current_turn']['buying_power'] = {
        'optional': player['current_turn']['buying_power'].get('optional', 0) + int(
            player['hand'][index].get('buyingPower', 0))}
    player['hand'][index]['played'] = True
    game['players'][game['curr_player']] = player
    return game


def buy_card(game, args):
    marketplace = game['marketplace']
    player = game['players'][game['curr_player']]
    index = int(args.get('index'))
    c = marketplace[index]
    marketplace[index] = decrement_qty(marketplace[index])
    player['discard'].append(c)
    use_action(player['current_turn'], 'buy')
    for i in range(int(c['costBuy'])):
        use_action(player['current_turn'], 'buying_power')
    game['marketplace'] = marketplace
    game['players'][game['curr_player']] = player
    return game


def draw_cards(game, args):
    player = game['players'][game['curr_player']]
    num_draw = int(args.get('num'))
    new_cards = []
    deck = player['deck']
    for i in range(num_draw):
        use_action(player['current_turn'], 'draw')
        if (len(deck) == 0):
            deck = deck_utils.shuffle(player['discard'], len(player['discard']))
            player['discard'] = []
        if (len(deck) > 0):
            new_cards.append(deck.pop())
    player['hand'] += new_cards
    game['players'][game['curr_player']] = player
    return game


def discard_card(game, args):
    player = game['players'][game['curr_player']]
    index = args.get('index')
    use_action(player['current_turn'], 'discard')
    player['discard'].append(player['hand'].pop(int(index)))
    game['players'][game['curr_player']] = player
    return game


def destroy_card(game, args):
    player = game['players'][game['curr_player']]
    index = args.get('index')
    use_action(player['current_turn'], 'destroy')
    game['destroy'].append(player['hand'].pop(int(index)))
    game['players'][game['curr_player']] = player
    return game


action_functions = {
    'play': play_card,
    'buy': buy_card,
    'draw': draw_cards,
    'discard': discard_card,
    'destroy': destroy_card
}
