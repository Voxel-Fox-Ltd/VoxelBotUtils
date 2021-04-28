from .buttons import ButtonStyle, Button, ButtonInteractionPayload


class ActionRow(object):

    def __init__(self, *components):
        self.components = list(components)

    def to_dict(self):
        return {
            "type": 1,
            "components": [i.to_dict() for i in self.components],
        }
