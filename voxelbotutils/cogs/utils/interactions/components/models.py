class BaseComponent(object):

    def to_dict(self):
        raise NotImplementedError()


class DisableableComponent(BaseComponent):

    def disable(self):
        self.disabled = True

    def enable(self):
        self.disabled = False


class ComponentHolder(BaseComponent):

    def disable_components(self):
        for i in self.components:
            if isinstance(i, DisableableComponent):
                i.disable()

    def enable_components(self):
        for i in self.components:
            if isinstance(i, DisableableComponent):
                i.enable()


class ActionRow(ComponentHolder):

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
