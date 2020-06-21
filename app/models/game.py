from flask_restx import fields
from . import card
from . import action


def TurnModel(api):
    m = {
        "pre": fields.List(fields.Nested(action.model(api))),
        "during": fields.List(fields.Nested(action.model(api))),
        "post": fields.List(fields.Nested(action.model(api))),
    }
    return api.model("turn", m)


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
        "marketplace": fields.List((DeckModel(api))),
        "discard": DeckModel(api),
        "destroy": DeckModel(api)
    }
    return m


def model(api):
    return api.model("game", GameModel(api))
