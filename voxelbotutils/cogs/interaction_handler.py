import inspect

from discord.ext import commands

from . import utils


class SlashCommandContext(utils.interactions.interaction_messageable.InteractionMessageable, utils.Context):
    pass


class InteractionHandler(utils.Cog):

    async def get_context_from_interaction(self, payload, *, cls=SlashCommandContext):
        """
        Make a context object from an interaction.
        """

        # command_args = [f"﹃{i['value']}﹄" for i in payload['data'].get('options', list())]  # ﹃﹄ are valid quotes for Dpy

        # Get the arguments from the payload
        command_name = payload['data']['name']
        if 'options' in payload['data']:
            payload_data_options = payload['data']
            while 'options' in payload_data_options:
                payload_data_options = payload_data_options['options']
                if isinstance(payload_data_options, list) and payload_data_options and 'options' in payload_data_options[0]:
                    payload_data_options = payload_data_options[0]
                    command_name += f" {payload_data_options['name']}"
                else:
                    break
        else:
            payload_data_options = list()

        # Put our options in a dict
        given_values = {}
        for i in payload_data_options:
            given_values[i['name']] = i['value']

        # Make a string view
        command_args = [f"{i['value']}" for i in payload_data_options]
        view = commands.view.StringView(f"/{command_name.rstrip()} {' '.join(command_args)}")
        self.logger.debug(f"Made up fake string for interaction command: {view.buffer}")

        # Get some objects we can use to make the interaction message
        state = self.bot._connection
        channel, _ = state._get_guild_channel(payload)

        # Make our fake message
        fake_message = utils.interactions.InteractionMessage(
            channel=channel,
            state=state,
            data=payload,
            content=view.buffer,
        )
        self.logger.debug("Made up fake message for interaction command")
        ctx = cls(prefix="/", view=view, bot=self.bot, message=fake_message)
        self.logger.debug("Made up fake context for interaction command")
        ctx.data = payload
        ctx.original_author_id = fake_message.author.id
        view.skip_string(ctx.prefix)
        invoker = view.get_word()

        # Make it work
        ctx.invoked_with = invoker
        ctx.command = self.bot.get_command(command_name)
        ctx.command_name = command_name
        ctx.given_values = given_values

        # Return context
        self.logger.debug("Returning context object")
        return ctx

    @utils.Cog.listener()
    async def on_socket_response(self, payload: dict):
        """
        Process any interaction create payloads we may receive.
        """

        if payload['t'] != 'INTERACTION_CREATE':
            return
        self.logger.debug("Received interaction payload %s" % (str(payload)))

        # See if it's a ping - it should _never_ be a ping, but let's put it here anyway
        if payload['d']['type'] == 1:
            return

        # See if it's a slash command
        elif payload['d']['type'] == 2:
            ctx = await self.get_context_from_interaction(payload['d'])

            # Invoke non-commands too
            if not ctx.command:
                self.logger.warning("No command found for interaction invoker %s" % (ctx.invoked_with))
                self.bot.dispatch("command_error", ctx, commands.CommandNotFound())
                return

            # Convert our stuff
            self.logger.debug("Invoking interaction context for command %s" % (ctx.command.name))
            # self.logger.debug(ctx.command)
            # self.logger.debug(ctx.command_name)
            # self.logger.debug(ctx.given_values)
            positional_converted = []
            kwarg_converted = {}
            for name, value in ctx.given_values.items():
                sig = ctx.command.clean_params[name]
                converter = ctx.command._get_converter(sig)
                v = await ctx.command.do_conversion(ctx, converter, value, sig)
                if sig.kind in [inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD]:
                    positional_converted.append(v)
                else:
                    kwarg_converted[name] = v

            # See if it can be run
            try:
                await ctx.command.can_run(ctx)
            except commands.CommandError as e:
                self.bot.dispatch("command_error", ctx, e)
                return

            # Try and run it
            try:
                await ctx.invoke(ctx.command, *positional_converted, **kwarg_converted)
            except commands.CommandError as e:
                self.bot.dispatch("command_error", ctx, e)
                return
            return

        # See if it was a clicked component
        elif payload['d']['type'] == 3:
            clicked_button_payload = utils.interactions.components.ComponentInteractionPayload.from_payload(
                payload['d'], self.bot._connection,
            )
            # clicked_button_payload._send_interaction_response_callback()
            self.bot.dispatch("button_click", clicked_button_payload)  # DEPRECATED PLEASE DO NOT USE
            self.bot.dispatch("component_interaction", clicked_button_payload)
            return

        # Something that we're unable to handle
        else:
            self.logger.warning("Invalid interaction type received - %d" % (payload['d']['type']))


def setup(bot: utils.Bot):
    x = InteractionHandler(bot)
    bot.add_cog(x)
