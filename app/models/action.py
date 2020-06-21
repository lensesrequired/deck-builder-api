from flask_restx import fields


class ActionType(fields.String):
    __schema_example__ = 'one of [draw, action, buy, discard, destroy]'


ActionModel = {
    "type": ActionType,
    "required": fields.boolean,
    "qty": fields.Integer
}


def model(api):
    return api.model("action", ActionModel)
