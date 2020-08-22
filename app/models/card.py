from flask_restx import fields
from . import action


def CardModel(api):
    m = {
        "id": fields.String,
        "modifiedAt": fields.String,
        "qty": fields.Integer,
        "art": fields.String,
        "name": fields.String,
        "actions": fields.List(fields.Nested(action.card_action(api))),
        "costBuy": fields.Integer(min=0),
        "buyingPower": fields.Integer,
        "victoryPoints": fields.Integer
    }
    return m


def model(api):
    return api.model("card", CardModel(api))
