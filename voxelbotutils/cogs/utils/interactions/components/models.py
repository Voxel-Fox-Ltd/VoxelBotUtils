import re
import typing
import json

import discord


def get_partial_emoji(emoji: typing.Union[str, discord.PartialEmoji]) -> discord.PartialEmoji:
    if isinstance(emoji, str):
        match = re.match(r'<(a?):([a-zA-Z0-9\_]+):([0-9]+)>$', emoji)
        if match:
            emoji_animated = bool(match.group(1))
            emoji_name = match.group(2)
            emoji_id = int(match.group(3))
            emoji = discord.PartialEmoji(
                name=emoji_name,
                animated=emoji_animated,
                id=emoji_id,
            )
    return emoji


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

    @classmethod
    def from_dict(cls, data):
        """
        Convert a response from the API into an object of this type.
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
