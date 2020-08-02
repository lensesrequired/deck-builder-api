## Known Bugs or Gotchas

1) There's very little type handling. If a user supplies the API bad data, it'll likely put them in the database but then throw errors later.
2) A game has an order it's supposed to happen in, but the API doesn't enforce that order. For example, if you get a few turns into the game, but then try to start the game again, it'll reset users and mess up the state of the game.
