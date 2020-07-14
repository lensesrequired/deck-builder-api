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
