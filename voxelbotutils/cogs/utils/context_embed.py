import random

import discord


class Embed(discord.Embed):
    """
    A small mod for discord.Embed that allows for some of the more common things
    that I tend to do with them.
    """

    def __init__(self, *args, use_random_colour:bool=False, **kwargs):
        """
        Args:
            *args: Default args that go do `discord.Embed`.
            use_random_colour (bool, optional): Whether or not to automatically use a random colour.
            **kwargs: Default args that go do `discord.Embed`.
        """

        super().__init__(*args, **kwargs)
        if use_random_colour:
            self.use_random_colour()

    def __enter__(self) -> 'Embed':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # :(
        pass

    def use_random_colour(self) -> 'Embed':
        """
        Sets the colour for the embed to a random one.

        Returns:
            Embed: The embed instance.
        """

        self.colour = random.randint(0, 0xffffff)
        return self

    def set_footer(self, text:str, *args, **kwargs) -> 'Embed':
        """
        Sets the footer of the embed.

        Args:
            text (str): The text to use in the footer.
            *args: Default args that go do `discord.Embed.set_footer`.
            **kwargs: Default args that go do `discord.Embed.set_footer`.

        Returns:
            Embed: The embed instance.
        """

        super().set_footer(*args, text=text, **kwargs)
        return self

    def set_image(self, url:str) -> 'Embed':
        """
        Sets the image of the embed.

        Args:
            url (str): The URL to set the image to.

        Returns:
            Embed: The embed instance.
        """

        super().set_image(url=url)
        return self

    def set_thumbnail(self, url:str) -> 'Embed':
        """
        Sets the thumbnail of the embed.

        Args:
            url (str): The URL to set the thumbnail to.

        Returns:
            Embed: The embed instance.
        """

        super().set_thumbnail(url=url)
        return self

    def set_author_to_user(self, user:discord.User, use_nick:bool = False) -> 'Embed':
        """
        Sets the author of the embed to a given Discord user.

        Args:
            user (discord.User): The user you want to set the author to.
            use_nick (bool): Whether to use the guild nickname or regular username.

        Returns:
            Embed: The embed instance.
        """

        if use_nick:
            name = user.display_name
        else:
            name = str(user)
        super().set_author(name=name, icon_url=user.avatar_url)
        return self

    def add_field(self, name:str, value:str, inline:bool=True) -> 'Embed':
        """
        Adds a field to the embed without using kwargs.

        Args:
            name (str): The name of the field.
            value (str): The value of the field.
            inline (bool, optional): Whether or not to set the field as inline.

        Returns:
            Embed: The embed instance.
        """

        super().add_field(name=name, value=value, inline=inline)
        return self

    def get_field_by_key(self, key:str) -> dict:
        """
        Return the data from a field given its key

        Args:
            key (str): The name of the field you want to get the data for

        Returns:
            dict: A dictionary of the attrs for that field

        Raises:
            KeyError: If the given key doesn't exist in the embed
        """

        for index, field in enumerate(self.fields):
            if field.name == key:
                return {'name': field.name, 'value': field.value, 'inline': field.inline}
        raise KeyError("Key not found in embed")

    def edit_field_by_index(self, index:int, *, name:str=None, value:str=None, inline:bool=None) -> 'Embed':
        """
        Edit a field in the embed using its index.

        Args:
            index (int): The index of the field you want to edit.
            name (str, optional): What you want to set the name to.
            value (str, optional): What you want to set the value to.
            inline (bool, optional): Whether or not the field should be inline.

        Returns:
            Embed: The embed instance.
        """

        field = self.fields[index]
        new_name = name or field.name
        new_value = value or field.value
        new_inline = inline if inline is not None else field.inline
        super().set_field_at(index, name=new_name, value=new_value, inline=new_inline)
        return self

    def edit_field_by_key(self, key:str, *, name:str=None, value:str=None, inline:bool=None) -> 'Embed':
        """
        Edit a field in the embed using its name as a key.

        Args:
            key (str): The key of the field to edit, based on its name.
            name (str, optional): What you want to set the name to.
            value (str, optional): What you want to set the value to.
            inline (bool, optional): Whether or not the field should be inline.

        Returns:
            Embed: The embed instance.

        Raises:
            KeyError: If the given key isn't present in the embed.
        """

        for index, field in enumerate(self.fields):
            if field.name == key:
                return self.edit_field_by_index(index, name=name, value=value, inline=inline)
        raise KeyError("Key not found in embed")
