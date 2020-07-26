from flask_restx import fields
from . import card
from . import action


def TurnModel(api):
    m = {
        "pre": fields.Nested(action.turn_action(api)),
        "during": fields.Nested(action.turn_action(api)),
        "post": fields.Nested(action.turn_action(api))
    }
    return api.model("turn", m)


def TriggerModel(api):
    m = {
        "'turn' or 'piles'": fields.Integer
    }
    return api.model("trigger", m)


def SettingsModel(api):
    m = {
        "num_players": fields.Integer(min=1),
        "starting_deck": DeckModel(api),
        "starting_hand_size": fields.Integer,
        "turn": fields.Nested(TurnModel(api))
    }
    return api.model("settings", m)


def PlayerModel(api):
    m = {
        "hand": DeckModel(api),
        "discard": DeckModel(api),
        "deck": DeckModel(api),
        "current_turn": fields.Integer(min=0)
    }
    return api.model("player", m)


def DeckModel(api):
    m = fields.List(fields.Nested(card.model(api)))
    return m


def GameModel(api):
    m = {
        "deck_id": fields.String,
        "settings": fields.Nested(SettingsModel(api)),
        "curr_player": fields.Integer(min=0),
        "players": fields.List(fields.Nested(PlayerModel(api))),
        "marketplace": DeckModel(api),
        "discard": DeckModel(api),
        "destroy": DeckModel(api)
    }
    return m


def model(api):
    return api.model("game", GameModel(api))


def settings(api):
    return api.model("game_settings", {
        "numPlayers": fields.Integer(min=1),
        "startingDeck": DeckModel(api),
        "handSize": fields.Integer,
        "turn": fields.Nested(TurnModel(api)),
        "end_trigger": fields.Nested(TriggerModel(api)),
        "marketplace": DeckModel(api)
    })
