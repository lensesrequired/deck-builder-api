def use_action(turn, action_type):
    # look for required and decrement that first
    for action in turn:
        if (action['type'] == action_type):
            if (action.get('required', False) and int(action['qty']) > 0):
                action['qty'] -= 1
                return
    for action in turn:
        if (action['type'] == action_type):
            action['qty'] -= 1
            return
    turn.append({'type': action_type, 'qty': -1})


def add_action(turn, action):
    # look for required and decrement that first
    for a in turn:
        if (a['type'] == action['type'] and a['required'] == action['required']):
            a['qty'] += int(action['qty'])
            return
    turn.append(action)


def equal(card1, card2):
    return (card1.name == card2.name and card1.art == card2.art)


def decrementQty(card):
    card['qty'] = int(card['qty']) - 1
    return card
