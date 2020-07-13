from random import randint


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
        points = sum([card['victoryPoints'] for card in all_cards])
        stats['player_points'][player['name']] = points
        if (points > stats['winner'][1]):
            stats['winner'] = (player['name'], points)
    return stats
