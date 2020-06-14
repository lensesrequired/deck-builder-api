from flask_restx import fields
import uuid
from models import action


class ActionType(fields.Integer):
    __schema_example__ = 'draw, action, buy'


class GUID(fields.String):
    def output(self, key, obj):
        return uuid.uuid1()


def ActionModel(api):
    m = {
        "additions": fields.List(fields.Nested(action.model(api))),
        "discardQty": fields.Integer(min=0),
        "discardRequired": fields.Boolean(default=True),
        "destroyQty": fields.Integer(min=0),
        "destroyRequired": fields.Boolean(default=True),
        "buyingPower": fields.Integer
    }
    return api.model("cardActions", m)


def CardModel(api):
    m = {
        "id": GUID,
        "art": fields.String,
        "name": fields.String,
        "actions": fields.Nested(ActionModel(api)),
        "costBuy": fields.Integer(min=0),
        "victoryPoints": fields.Integer
    }
    return m


def model(api):
    return api.model("card", CardModel(api))
