from .buttons import ButtonStyle, Button, ButtonInteractionPayload


class ActionRow(object):

    def __init__(self, *components):
        self.components = list(components)

    def to_dict(self):
        return {
            "type": 1,
            "components": [i.to_dict() for i in self.components],
        }
    
    def __getitem__(self, custom_id: str):
        for i in self.components:
            if getattr(i, "custom_id", None) == custom_id:
                return i
        
        raise KeyError(f"There is no component with the custom ID {custom_id}")
        
