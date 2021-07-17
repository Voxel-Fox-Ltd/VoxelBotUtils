import typing

from .models import BaseComponent, ComponentHolder
from .buttons import Button
from .select_menu import SelectMenu


# This'll be a dict of `type: component`, defined here
# for typing purposes but filled at the bottom
component_types: typing.Dict[int, BaseComponent] = {}


class ActionRow(ComponentHolder):
    """
    The main UI component for adding and ordering components on Discord
    messages.
    """

    TYPE = 1
    WIDTH = 5

    def to_dict(self):
        return {
            "type": self.TYPE,
            "components": [i.to_dict() for i in self.components],
        }

    @classmethod
    def from_dict(cls, data: list):
        components = data.get("components", list())
        new_components = []
        for i in components:
            component_type = component_types.get(i['type'], BaseComponent)
            if component_type == BaseComponent:
                v = BaseComponent()
                v.custom_id = i['custom_id']
            else:
                v = component_type.from_dict(i)
            new_components.append(v)
        return cls(*new_components)


class MessageComponents(ComponentHolder):
    """
    A set of components that can be added to a message.
    """

    def to_dict(self):
        return [i.to_dict() for i in self.components]

    @classmethod
    def from_dict(cls, data: dict):
        new_components = []
        for i in data:
            component_type = component_types.get(i['type'], BaseComponent)
            if component_type == BaseComponent:
                v = BaseComponent()
                v.custom_id = i['custom_id']
            else:
                v = component_type.from_dict(i)
            new_components.append(v)
        return cls(*new_components)

    @classmethod
    def boolean_buttons(cls, yes_id: str = None, no_id: str = None):
        """
        Return a set of message components with yes/no buttons, ready for use. If provided, the given IDs
        will be used for the buttons. If not, the button custom IDs will be set to the strings
        "YES" and "NO".

        Args:
            yes_id (str, optional): The custom ID of the yes button.
            no_id (str, optional): The custom ID of the no button.
        """

        from .buttons import Button, ButtonStyle
        return cls(
            ActionRow(
                Button("Yes", style=ButtonStyle.SUCCESS, custom_id=yes_id or "YES"),
                Button("No", style=ButtonStyle.DANGER, custom_id=no_id or "NO"),
            ),
        )

    @classmethod
    def add_buttons_with_rows(cls, *buttons: Button):
        """
        Adds a list of buttons, breaking into a new :class:`ActionRow` automatically when it contains 5
        buttons. This does *not* check that you've added fewer than 5 rows.

        Args:
            *buttons (Button): The buttons that you want to have added.
        """

        v = cls()
        while buttons:
            v.add_component(ActionRow(*buttons[:5]))
            buttons = buttons[5:]
        return v


component_types = {
    1: ActionRow,
    2: Button,
    3: SelectMenu,
}
