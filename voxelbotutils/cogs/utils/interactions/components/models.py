import typing


class BaseComponent(object):
    """
    A message component for Discord UI interactions.
    """

    def to_dict(self) -> dict:
        """
        Convert the current component object into a dictionary that we can
        send to Discord as a payload.
        """

        raise NotImplementedError()


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

    def get_component(self, custom_id: str) -> typing.Optional[BaseComponent]:
        """
        Get a component from the internal :attr:`components` list using its `custom_id` attribute.

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


class MessageComponents(ComponentHolder):
    """
    A list of components that are to be added to a message.
    """

    def to_dict(self):
        return [i.to_dict() for i in self.components]


class ActionRow(ComponentHolder):
    """
    The main UI component for adding and ordering components on Discord
    messages.
    """

    def to_dict(self):
        return {
            "type": 1,
            "components": [i.to_dict() for i in self.components],
        }
