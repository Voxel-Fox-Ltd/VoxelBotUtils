import asyncio
import inspect

from discord.ext import commands

from . import utils as vbu


class SlashCommandContext(vbu.interactions.interaction_messageable.InteractionMessageable, vbu.Context):
    pass


class InteractionHandler(vbu.Cog):

    async def get_context_from_interaction(self, payload, *, cls=SlashCommandContext):
        """
        Make a context object from an interaction.
        """

        # Try and create the command name
        command_name = payload['data']['name']
        data = payload['data']
        options = list()
        while True:
            if "options" not in data:
                break
            if data['options'][0]['type'] in [1, 2]:
                data = data['options'][0]
                command_name += f" {data['name']}"
            else:
                options = data['options']
                break

        # Put our options in a dict
        given_values = {}
        for i in options:
            value = str(i['value'])
            # if isinstance(value, str):
            given_values[i['name']] = value.strip()
            # else:
            #     given_values[i['name']] = value

        # If we have a target_id, then the interaction is a context menu
        if 'target_id' in payload['data']:
            given_values[None] = payload['data']['target_id']

        # Make a string view
        command_args = [f"{i['value']}" for i in options]
        view = commands.view.StringView(f"/{command_name.rstrip()} {' '.join(command_args)}")
        self.logger.debug(f"Made up fake string for interaction command: {view.buffer}")

        # Get some objects we can use to make the interaction message
        state = self.bot._connection
        channel, _ = state._get_guild_channel(payload)

        # Make our fake message
        fake_message = vbu.interactions.InteractionMessage(
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
        if ctx.command is None and 'target_id' in payload['data']:
            for i in self.bot.walk_commands():
                if getattr(i, "context_command_name", None) == command_name:
                    ctx.command = i
                    break
        ctx.command_name = command_name
        ctx.given_values = given_values
        ctx.is_interaction = True

        # Return context
        self.logger.debug("Returning context object")
        return ctx

    async def parse_arguments(self, ctx: vbu.Context):
        """
        Parse the arguments for a given context.
        """

        # Convert our given values
        self.logger.debug("Converterting interaction args for command %s" % (ctx.command.name))
        ctx.args = [ctx] if ctx.command.cog is None else [ctx.command.cog, ctx]
        ctx.kwargs = {}
        for name, value in ctx.given_values.items():
            if name is None:
                for name, sig in ctx.command.clean_params.items():
                    break  # Just get the first param - deliberately shadow "name"
            else:
                sig = ctx.command.clean_params[name]
            converter = ctx.command._get_converter(sig)
            v = await ctx.command.do_conversion(ctx, converter, value, sig)  # Could raise; that's fine
            if sig.kind in [inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD]:
                ctx.args.append(v)
            else:
                ctx.kwargs[name] = v

    @vbu.Cog.listener()
    async def on_component_interaction(self, payload: vbu.ComponentInteractionPayload):
        if not payload.component.custom_id.startswith("RUNCOMMAND"):
            return
        command_name = payload.component.custom_id[len("RUNCOMMAND "):]
        command = self.bot.get_command(command_name)
        if command:
            payload.author = payload.user
            payload.command = command
            if command.cog:
                payload.args = [command.cog, payload]
            else:
                payload.args = [payload]
            payload.kwargs = {}
            await self.run_command(payload)

    async def run_command(self, ctx):
        self.bot.dispatch("command", ctx)
        try:
            if await ctx.command.can_run(ctx):
                try:
                    await ctx.command.callback(*ctx.args, **ctx.kwargs)
                except commands.CommandError:
                    ctx.command_failed = True
                    raise
                except asyncio.CancelledError:
                    ctx.command_failed = True
                    return
                except Exception as exc:
                    ctx.command_failed = True
                    raise commands.CommandInvokeError(exc) from exc
                finally:
                    if ctx.command._max_concurrency is not None:
                        await ctx.command._max_concurrency.release(ctx)
                    await ctx.command.call_after_hooks(ctx)
            else:
                raise commands.CheckFailure()
        except commands.CommandError as e:
            await ctx.command.dispatch_error(ctx, e)
        else:
            self.bot.dispatch("command_completion", ctx)

    @vbu.Cog.listener()
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

            # Raise a CommandNotFound
            if ctx.command is None:
                if ctx.invoked_with:
                    exc = commands.CommandNotFound('Command "{}" is not found'.format(ctx.invoked_with))
                    self.bot.dispatch('command_error', ctx, exc)
                return

            # Parse cooldowns and args
            if ctx.command._max_concurrency is not None:
                await ctx.command._max_concurrency.acquire(ctx)
            try:
                if ctx.command.cooldown_after_parsing:
                    await self.parse_arguments(ctx)
                    await ctx.command._prepare_cooldowns(ctx)
                else:
                    await ctx.command._prepare_cooldowns(ctx)
                    await self.parse_arguments(ctx)
                await ctx.command.call_before_hooks(ctx)
            except commands.CommandError as e:
                await ctx.command.dispatch_error(ctx, e)
                return
            except Exception as e:
                if ctx.command._max_concurrency is not None:
                    await ctx.command._max_concurrency.release(ctx)
                await ctx.command.dispatch_error(ctx, e)
                return

            # And invoke
            self.logger.debug("Invoking interaction context for command %s" % (ctx.command.name))
            await self.run_command(ctx)

        # See if it was a clicked component
        elif payload['d']['type'] == 3:
            clicked_button_payload = vbu.interactions.components.ComponentInteractionPayload.from_payload(
                payload['d'], self.bot,
            )  # TODO should this be a webhook connection state?
            self.bot.dispatch("button_click", clicked_button_payload)  # DEPRECATED PLEASE DO NOT USE
            self.bot.dispatch("component_interaction", clicked_button_payload)
            return

        # Something that we're unable to handle
        else:
            self.logger.warning("Invalid interaction type received - %d" % (payload['d']['type']))


def setup(bot: vbu.Bot):
    x = InteractionHandler(bot)
    bot.add_cog(x)
