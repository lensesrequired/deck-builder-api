from flask_restx import fields


class ActionType(fields.String):
    __schema_example__ = 'one of [draw, action, buy, discard, destroy]'


ActionModel = {
    "type": ActionType,
    "required": fields.Boolean,
    "qty": fields.Integer
}


def card_action(api):
    return api.model("card_action", ActionModel)


def turn_action_qtys(api):
    m = {
        "required": fields.Integer,
        "optional": fields.Integer
    }
    return api.model("turn_action_qtys", m)


def turn_action(api):
    m = {
        "any of [draw, action, buy, discard, destroy]": fields.Nested(turn_action_qtys(api)),
    }
    return api.model("turn_action", m)
