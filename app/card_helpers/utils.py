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
