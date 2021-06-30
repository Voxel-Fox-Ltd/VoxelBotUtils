Menus Howto
##########################################

Menus are a pain to implement yourself in a lot of cases, so VoxelBotUtils does its best to handle those for you in an intuitive way.

Making a Menu
------------------------------------------

When it boils down to it, a menu is a list of options. This is how VBU implements them as well - a menu instance is simply a list of options that is presented to the user.

For starters, here's a menu with a single option in it:

.. code-block:: python

    # Store our menu instance in a variable
    settings_menu = vbu.menus.Menu(

        # Our menu contains an option
        vbu.menus.Option(

            # This is what is displayed in the presented embed
            # Can be a function taking ctx, or a string
            display=lambda ctx: f"Favourite role (currently {ctx.bot.guild_settings[ctx.guild.id]['favourite_role']})",

            # This is what is shown on the button
            component_display="Favourite role",

            # This is a list of things that the user should be asked for
            converters=[

                # Make a converter instance
                vbu.menus.Converter(

                    # This is the message that's sent to the user
                    prompt="What role is your favourite?",

                    # The converter that we're using to convert the user's input
                    converter=discord.Role,

                    # The message to be sent if the converter times out
                    timeout_message="Timed out asking for old role removal.",
                ),
            ],

            # These are [async] functions that are called when the converters pass
            callback=vbu.menus.Menu.callbacks.set_table_column(vbu.menus.DataLocation.GUILD, "guild_settings", "remove_old_roles"),
            cache_callback=vbu.menus.Menu.callbacks.set_cache_from_key(vbu.menus.DataLocation.GUILD, "remove_old_roles"),
        ),
    )
