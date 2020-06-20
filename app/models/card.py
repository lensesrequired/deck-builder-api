from flask_restx import fields
import uuid
from . import action


class GUID(fields.String):
    def output(self, key, obj):
        return uuid.uuid1()


def CardModel(api):
    m = {
        "id": GUID,
        "art": fields.String,
        "name": fields.String,
        "actions": fields.List(fields.Nested(action.model(api))),
        "costBuy": fields.Integer(min=0),
        "buyingPower": fields.Integer,
        "victoryPoints": fields.Integer
    }
    return m


def model(api):
    return api.model("card", CardModel(api))
