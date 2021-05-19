import typing
import json


class BaseComponent(object):
    """
    The base message component for Discord UI interactions.
    """

    def to_dict(self) -> dict:
        """
        Convert the current component object into a dictionary that we can
        send to Discord as a payload.
        """

        raise NotImplementedError()

    def __eq__(self, other) -> bool:
        """
        Checks if two components are equal to one another.
        """

        if not isinstance(other, BaseComponent):
            raise TypeError("Can't compare {} and {}".format(self.__class__, other.__class__))
        return self.to_dict() == other.to_dict()

    def __hash__(self):
        """:meta private:"""

        return hash(json.dumps(self.to_dict(), sort_keys=True))


class DisableableComponent(BaseComponent):
    """
    A message component that has a `disabled` flag.
    """

    def disable(self) -> None:
        """
        Set the disabled flag on the current component.
        """

        self.disabled = True

    def enable(self) -> None:
        """
        Unset the disabled flag on the current component.
        """

        self.disabled = False


class ComponentHolder(BaseComponent):
    """
    A message component that holds other message components.
    """

    def __init__(self, *components: typing.List[BaseComponent]):
        """
        Args:
            *components: A list of the components that this component holder holds.
        """

        self.components = list(components)

    def add_component(self, component: BaseComponent):
        """
        Adds a component to this holder.

        Args:
            component (BaseComponent): The component that you want to add.
        """

        self.components.append(component)
        return self

    def remove_component(self, component: BaseComponent):
        """
        Removes a component from this holder.

        Args:
            component (BaseComponent): The component that you want to remove.
        """

        self.components.remove(component)
        return self

    def disable_components(self) -> None:
        """
        Disables all of the components inside this component holder that
        inherit from :class:`DisableableComponent`.
        """

        for i in self.components:
            if isinstance(i, ComponentHolder):
                i.disable_components()
            elif isinstance(i, DisableableComponent):
                i.disable()
        return self

    def enable_components(self) -> None:
        """
        Enables all of the components inside this component holder that
        inherit from :class:`DisableableComponent`.
        """

        for i in self.components:
            if isinstance(i, ComponentHolder):
                i.enable_components()
            elif isinstance(i, DisableableComponent):
                i.enable()
        return self

    def get_component(self, custom_id: str) -> typing.Optional[BaseComponent]:
        """
        Get a component from the internal :attr:`components` list using its :attr:`custom_id` attribute.

        Args:
            custom_id (str): The ID of the component that you want to find.

        Returns:
            typing.Optional[BaseComponent]: The component that was found, if any.
        """

        for i in self.components:
            if isinstance(i, ComponentHolder):
                v = i.get_component(custom_id)
                if v:
                    return v
            else:
                if i.custom_id == custom_id:
                    return i
        return None


class ActionRow(ComponentHolder):
    """
    The main UI component for adding and ordering components on Discord
    messages.
    """

    TYPE = 1

    def to_dict(self):
        return {
            "type": self.TYPE,
            "components": [i.to_dict() for i in self.components],
        }


class MessageComponents(ComponentHolder):
    """
    A set of components that can be added to a message.
    """

    def to_dict(self):
        return [i.to_dict() for i in self.components]

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
    def add_buttons_with_rows(cls, *buttons: BaseComponent):
        """
        Adds a list of buttons, breaking into a new :class:`ActionRow` automatically when it contains 5
        buttons. This does *not* check that you've added fewer than 5 rows.

        Args:
            *buttons (BaseComponent): The buttons that you want to have added.
        """

        v = cls()
        while buttons:
            v.add_component(ActionRow(*buttons[:5]))
            buttons = buttons[:5]
        return v
