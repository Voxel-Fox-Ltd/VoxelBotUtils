import asyncio
import contextlib
import copy
import io
import os
import json
import textwrap
import traceback
import typing
import inspect

import discord
from discord.ext import commands

from . import utils


class OwnerOnly(utils.Cog, command_attrs={'hidden': True, 'add_slash_command': False}):
    """
    Handles commands that only the owner should be able to run.
    """

    @commands.command(aliases=['src'], cls=utils.Command)
    @commands.is_owner()
    @commands.bot_has_permissions(send_messages=True, attach_files=True, add_reactions=True)
    async def source(self, ctx:utils.Context, *, command_name:str):
        """
        Shows you the source for a given command.
        """

        command = self.bot.get_command(command_name)
        if command is None:
            return await ctx.send(f"I couldn't find a command named `{command_name}`.", allowed_mentions=discord.AllowedMentions.none())
        data = textwrap.dedent(inspect.getsource(command.callback))
        lines = data.strip().split("\n")
        current, last = "", ""
        pages = []
        for line in lines:
            current += f"{line}\n"
            if len(current) >= 1950:
                pages.append(f"```py\n{last}\n```")
                current = line
            last = current
        if last:
            pages.append(f"```py\n{last}\n```")

        message = await ctx.send(pages[0])

        # List of valid emojis the user can react with
        validEmoji = [
            "\N{BLACK LEFT POINTING TRIANGLE}",
            "\N{BLACK RIGHT POINTING TRIANGLE}",
            "\N{WHITE HEAVY CHECK MARK}"
        ]

        # Reacts to the initial message with left arrow, right arrow, and check mark
        for i in valid_emoji:
            try:
                await message.add_reaction(i)
            except discord.HTTPException:
                return

        # Loops until checkmark is reacted
        index = 0
        while True:

            # Checks that author is who typed the command and that the emoji reacted by the user is in validEmoji
            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in validEmoji

            # Waits for the reaction from the user
            try:
                reaction, _ = await self.bot.wait_for('reaction_add', timeout=300.0, check=check)
            except asyncio.TimeoutError:
                reaction.emoji = valid_emoji[2]

            # Checks which emoji was reacted and add to the index
            if reaction.emoji == valid_emoji[0]:
                index += 1
            if reaction.emoji == valid_emoji[1]:
                index -= 1
            if reaction.emoji == valid_emoji[2]:
                break

            # See if our index has changed
            index = max(0, index)
            index = min(len(pages), index)
            if new_index == index:
                continue
            else:
                index = new_index

            # Update the message
            try:
                await message.edit(content=pages[index])
            except discord.HTTPException:
                return

        # Removes the reactions from the initial message
        for i in valid_emoji:
            try:
                await message.remove_reaction(i)
            except discord.HTTPException:
                pass

    @commands.command(aliases=['pm', 'dm', 'send'], cls=utils.Command)
    @commands.is_owner()
    @commands.bot_has_permissions(send_messages=True, add_reactions=True)
    async def message(self, ctx:utils.Context, snowflake:int, *, content:str=None):
        """
        DMs a user the given content.
        """

        # Work out what we're going to use to convert the snowflake
        converters = [
            self.bot.get_user,
            self.bot.get_channel,
            self.bot.fetch_user,
            self.bot.fetch_channel,
        ]

        # Let's run our converters baybee
        sendable = None
        for method in converters:
            try:
                sendable = method(snowflake)
                if asyncio.iscoroutine(sendable):
                    sendable = await sendable
            except discord.HTTPException:
                sendable = None
            if sendable is not None:
                break

        # Make sure we have somewhere to send to
        if sendable is None:
            return await ctx.send(f"I couldn't work out where `{snowflake}` is meant to refer to.")

        # Set up what we want to send
        payload = {
            "content": content,
            "files": list(),
        }

        # Add the attachments of the original message
        for attachment in ctx.message.attachments:
            async with self.bot.session.get(attachment.url) as r:
                file_bytes = await r.read()
            image_file = io.BytesIO(file_bytes)
            payload["files"].append(discord.File(image_file, filename=attachment.filename))

        # And send our data
        try:
            await sendable.send(**payload)
        except discord.HTTPException as e:
            return await ctx.send(f"I couldn't send that message - `{e}`")
        await ctx.okay()

    def _cleanup_code(self, content):
        """Automatically removes code blocks from the code."""

        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            if content[-4] == '\n':
                return '\n'.join(content.split('\n')[1:-1])
            return '\n'.join(content.split('\n')[1:]).rstrip('`')

        # remove `foo`
        return content.strip('` \n')

    @commands.command(aliases=['evall', 'eval'], cls=utils.Command)
    @commands.is_owner()
    @commands.bot_has_permissions(send_messages=True)
    async def ev(self, ctx:utils.Context, *, content:str):
        """
        Evaluates some Python code.

        Gracefully stolen from Rapptz ->
        https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/admin.py#L72-L117
        """

        # Make the environment
        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            'self': self,
        }
        env.update(globals())

        # Make code and output string
        content = self._cleanup_code(content)
        code = f'async def func():\n{textwrap.indent(content, "  ")}'

        # Make the function into existence
        stdout = io.StringIO()
        try:
            exec(code, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```', embeddify=False)

        # Grab the function we just made and run it
        func = env['func']
        try:
            # Shove stdout into StringIO
            with contextlib.redirect_stdout(stdout):
                ret = await func()
        except Exception:
            # Oh no it caused an error
            stdout_value = stdout.getvalue() or None
            return await ctx.send(f'```py\n{stdout_value}\n{traceback.format_exc()}\n```', embeddify=False)

        # Oh no it didn't cause an error
        stdout_value = stdout.getvalue() or None

        # Give reaction just to show that it ran
        try:
            await ctx.okay()
        except discord.HTTPException:
            pass

        # If the function returned nothing
        if ret is None:
            # It might have printed something
            if stdout_value is not None:
                await ctx.send(f'```py\n{stdout_value}\n```', embeddify=False)
            return

        # If the function did return a value
        result_raw = stdout_value or ret  # What's returned from the function
        result = str(result_raw)  # The result as a string
        if result_raw is None:
            return
        text = f'```py\n{result}\n```'
        if type(result_raw) == dict:
            try:
                result = json.dumps(result_raw, indent=4)
            except Exception:
                pass
            else:
                text = f'```json\n{result}\n```'

        # Output to chat
        if len(text) > 2000:
            try:
                return await ctx.send(file=discord.File(io.StringIO(result), filename='ev.txt'))
            except discord.HTTPException:
                return await ctx.send("I don't have permission to attach files here.", embeddify=False)
        else:
            return await ctx.send(text, embeddify=False)

    @commands.command(aliases=['rld', 'rl'], cls=utils.Command)
    @commands.is_owner()
    @commands.bot_has_permissions(send_messages=True)
    async def reload(self, ctx:utils.Context, *cog_name:str):
        """
        Unloads and reloads a cog from the bot.
        """

        # Get a list of cogs to reload
        cog_name = 'cogs.' + '_'.join([i for i in cog_name])
        if cog_name == 'cogs.*':
            cog_list = [i for i in self.bot.get_extensions() if i.startswith('cogs.')]
        else:
            cog_list = [cog_name]

        # Reload our cogs
        reloaded_cogs = []
        for cog in cog_list:
            try:
                self.bot.load_extension(cog)
                reloaded_cogs.append(cog)
            except commands.ExtensionAlreadyLoaded:
                try:
                    self.bot.reload_extension(cog)
                    reloaded_cogs.append(cog)
                except Exception:
                    await ctx.send(f"Error loading cog `{cog}`: ```py\n{traceback.format_exc()}```")
            except Exception:
                await ctx.send(f"Error loading cog `{cog}`: ```py\n{traceback.format_exc()}```")

        # Output which cogs have been reloaded
        if len(cog_list) == 1:
            await ctx.send(f"Reloaded: `{cog_list[0]}`")
        else:
            await ctx.send("Reloaded:\n`" + "`\n`".join(cog_list) + "`")
        return

    @commands.command(cls=utils.Command, aliases=['downloadcog', 'dlcog', 'download', 'dl', 'stealcog'])
    @commands.is_owner()
    async def downloadfile(self, ctx:utils.Context, url:str, file_folder:typing.Optional[str]):
        """Download a cog from github"""

        # Convert github link to a raw link and grab contents
        raw_url = url.replace("/blob", "").replace("github.com", "raw.githubusercontent.com")
        headers = {"User-Agent": f"Discord Bot - {self.bot.user}"}
        async with self.bot.session.get(raw_url, headers=headers) as r:
            text = await r.text()

        # Work out our filename/path
        file_name = raw_url[raw_url.rfind("/") + 1:]
        if file_folder is None:
            file_folder = "cogs"
        file_folder = file_folder.rstrip("/")
        file_path = f"{file_folder}/{file_name}"

        # Create the file and dump the github content in there
        try:
            with open(file_path, "x", encoding="utf-8") as n:
                n.write(text)
        except FileExistsError:
            return await ctx.send("The file you tried to download was already downloaded.")

        # If it wasn't loaded into the cogs folder, we're probably fine
        if file_folder != "cogs":
            return await ctx.send(f"Downloaded the `{file_name}` file, and successfully saved as `{file_path}`.")

        # Load the cog
        errored = True
        try:
            self.bot.load_extension(f"cogs.{file_name[:-3]}")
            errored = False
        except commands.ExtensionNotFound:
            await ctx.send("Extension could not be found. Extension has been deleted.")
        except commands.ExtensionAlreadyLoaded:
            await ctx.send("The extension you tried to download was already running. Extension has been deleted.")
        except commands.NoEntryPointError:
            await ctx.send("No added setup function. Extension has been deleted.")
        except commands.ExtensionFailed:
            await ctx.send("Extension failed for some unknown reason. Extension has been deleted.")
        if errored:
            os.remove(file_path)
            return

        # And done
        await ctx.send(f"Downloaded the `{file_name}` cog, saved as `{file_path}`, and loaded successfully into the bot.")

    @commands.command(cls=utils.Command)
    @commands.is_owner()
    @commands.bot_has_permissions(send_messages=True)
    async def runsql(self, ctx:utils.Context, *, sql:str):
        """
        Runs a line of SQL into the database.
        """

        # Remove our backticks
        sql = self._cleanup_code(sql)

        # Get the data we asked for
        async with self.bot.database() as db:
            rows = await db(sql.format(guild=None if ctx.guild is None else ctx.guild.id, author=ctx.author.id, channel=ctx.channel.id))
        if not rows:
            return await ctx.send("No content.")

        # Set up some metadata for us to format things nicely
        headers = list(rows[0].keys())
        column_widths = {i: len(i) for i in headers}
        lines = []

        # See how long our lines are
        for row in rows:
            for header in headers:
                column_widths[header] = max([column_widths[header], len(str(row[header]))])

        # Work out our rows
        for row in rows:
            working = ""
            for header in headers:
                working += format(str(row[header]), f" <{column_widths[header]}") + "|"
            lines.append(working[:-1])

        # Add on our headers
        header_working = ""
        spacer_working = ""
        for header in headers:
            header_working += format(header, f" <{column_widths[header]}") + "|"
            spacer_working += "-" * column_widths[header] + "+"
        lines.insert(0, spacer_working[:-1])
        lines.insert(0, header_working[:-1])

        # Send it out
        string_output = '\n'.join(lines)
        try:
            await ctx.send(f"```\n{string_output}```", embeddify=False)
        except discord.HTTPException:
            file = discord.File(io.StringIO(string_output), filename="runsql.txt")
            await ctx.send(file=file)

    @commands.group(cls=utils.Group)
    @commands.is_owner()
    @commands.bot_has_permissions(send_messages=True)
    async def botuser(self, ctx:utils.Context):
        """
        A parent command for the bot user configuration section.
        """

        pass

    @botuser.command(name='name', aliases=['username'], cls=utils.Command)
    @commands.is_owner()
    @commands.bot_has_permissions(send_messages=True)
    async def botuser_name(self, ctx:utils.Context, *, username:str):
        """
        Lets you set the username for the bot account.
        """

        if len(username) > 32:
            return await ctx.send('That username is too long.')
        await self.bot.user.edit(username=username)
        await ctx.send('Done.')

    @botuser.command(name='avatar', aliases=['photo', 'image', 'picture'], cls=utils.Command)
    @commands.is_owner()
    @commands.bot_has_permissions(send_messages=True)
    async def botuser_avatar(self, ctx:utils.Context, *, image_url:typing.Optional[str]):
        """
        Lets you set the profile picture of the bot.
        """

        if image_url is None:
            try:
                image_url = ctx.message.attachments[0].url
            except IndexError:
                return await ctx.send("You need to provide an image.")

        async with self.bot.session.get(image_url) as r:
            image_content = await r.read()
        await self.bot.user.edit(avatar=image_content)
        await ctx.send('Done.')

    @botuser.command(name='activity', aliases=['game'], cls=utils.Command)
    @commands.is_owner()
    @commands.bot_has_permissions(send_messages=True)
    async def botuser_activity(self, ctx:utils.Context, activity_type:str, *, name:typing.Optional[str]):
        """
        Changes the activity of the bot.
        """

        if name:
            activity = discord.Activity(name=name, type=getattr(discord.ActivityType, activity_type.lower()))
        else:
            return await self.bot.set_default_presence()
        await self.bot.change_presence(activity=activity, status=self.bot.guilds[0].me.status)

    @botuser.command(name='status', cls=utils.Command)
    @commands.is_owner()
    @commands.bot_has_permissions(send_messages=True)
    async def botuser_status(self, ctx:utils.Context, status:str):
        """
        Changes the online status of the bot.
        """

        status = getattr(discord.Status, status.lower())
        await self.bot.change_presence(activity=self.bot.guilds[0].me.activity, status=status)

    @commands.command(cls=utils.Command, aliases=['sudo'])
    @commands.is_owner()
    @commands.bot_has_permissions(send_messages=True)
    async def su(self, ctx, who:discord.User, *, command:str):
        """
        Run a command as another user.
        """

        # Make a copy of the message so we can pretend the other user said it
        msg = copy.copy(ctx.message)

        # Change the author and content
        try:
            msg.author = ctx.guild.get_member(who.id) or await ctx.guild.fetch_member(who.id) or who
        except discord.HTTPException:
            msg.author = who
        msg.content = ctx.prefix + command

        # Make a context
        new_ctx = await self.bot.get_context(msg, cls=type(ctx))
        new_ctx.original_author_id = ctx.original_author_id

        # Invoke it dab
        await self.bot.invoke(new_ctx)

    @commands.command(cls=utils.Command, aliases=['sh'])
    @commands.is_owner()
    @commands.bot_has_permissions(send_messages=True)
    async def shell(self, ctx, *, command:str):
        """
        Run a shell command.
        """

        # Run stuff
        proc = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

        # Send initial message
        current_data = f"$ {command}\n\n"
        m = await ctx.send(f"```\n{current_data}```", embeddify=False)

        # Woah I do this a few times so let's put it in a function
        async def get_process_data(proc):
            stdout = await proc.stdout.read()
            stderr = await proc.stderr.read()
            return stdout.decode() + stderr.decode()

        # Grab new data
        while proc.returncode is None:
            new_lines = await get_process_data(proc)
            if new_lines:
                current_data += new_lines + '\n'
                await m.edit(content=f"```\n{current_data[-1900:]}```")
            await asyncio.sleep(1)

        # Make sure we got all the data
        new_lines = await get_process_data(proc)
        if new_lines:
            current_data += new_lines + '\n'
        current_data += f'[RETURN CODE {proc.returncode}]'
        await m.edit(content=f"```\n{current_data[-1900:]}```")

        # And now we done
        try:
            await m.add_reaction("\N{OK HAND SIGN}")
        except discord.HTTPException:
            pass

    @commands.group(cls=utils.Group)
    @commands.is_owner()
    async def export(self, ctx:utils.Context):
        """
        The parent group for the export commands.
        """

        pass

    @export.command(cls=utils.Command, name="commands")
    @commands.bot_has_permissions(send_messages=True, attach_files=True)
    @commands.is_owner()
    async def export_commands(self, ctx:utils.Context):
        """
        Exports the commands for the bot as a markdown file.
        """

        # Set up output
        lines = [f"# {self.bot.user.name} Commands\n"]

        # Work out prefix
        prefix = self.bot.config.get('default_prefix', ctx.clean_prefix)
        if isinstance(prefix, (list, tuple,)):
            prefix = prefix[0]

        # Go through the cogs
        for cog_name, cog in sorted(self.bot.cogs.items()):
            if cog_name == 'Help':
                continue

            # Go through the commands
            visible_commands = await self.bot.help_command.filter_commands_classmethod(ctx, cog.get_commands())
            if not visible_commands:
                continue

            # Add lines
            lines.append(f"## {cog_name}\n")
            for command in visible_commands:
                lines.append(f"* `{prefix}{command.name} {command.signature}".rstrip() + '`')
                lines.append(f"\t* {command.help}")

        # Output file
        await ctx.send(file=discord.File(io.StringIO('\n'.join(lines)), filename="commands.md"))

    @export.command(cls=utils.Command, name="guild")
    @commands.bot_has_permissions(send_messages=True, attach_files=True)
    @utils.checks.is_config_set('database', 'enabled')
    @commands.is_owner()
    async def export_guild(self, ctx:utils.Context, guild_id:typing.Optional[int]):
        """
        Exports data for a given guild from the database.

        Autoamtically searches for any public tables with a `guild_id` column, and then exports that as a
        file of "insert into" statements for you to use.
        """

        # Open db connection
        db = await self.bot.database.get_connection()

        # Get the tables that we want to export
        table_names = await db("SELECT DISTINCT table_name FROM INFORMATION_SCHEMA.COLUMNS WHERE table_schema='public' AND column_name='guild_id'")

        # Go through and make our insert statements
        insert_statements = []
        for table in table_names:

            # Select the data we want to export
            rows = await db("SELECT * FROM {} WHERE guild_id=$1".format(table['table_name']), guild_id or ctx.guild.id)
            for row in rows:
                cols = []
                datas = []

                # Add that data to a big ol list
                for col, data in row.items():
                    cols.append(col)
                    datas.append(data)
                insert_statements.append(
                    (
                        f"INSERT INTO {table['table_name']} ({', '.join(cols)}) VALUES ({', '.join('$' + str(i) for i, _ in enumerate(datas, start=1))});",
                        datas,
                    )
                )

        # Wew nice
        await db.disconnect()

        # Make sure we have some data
        if not insert_statements:
            return await ctx.send("This guild has no non-default settings.")

        # Time to make a script
        file_content = """
            import datetime

            DATA = (
                {data},
            )

            async def main():
                import asyncpg
                conn = await asyncpg.connect(
                    user="{user}",
                    password="",
                    database="{database}",
                    port={port},
                    host="{host}"
                )
                for query, data in DATA:
                    try:
                        await conn.execute(query, *data)
                    except Exception as e:
                        print(e)
                await conn.close()
                print("Done.")

            if __name__ == "__main__":
                import asyncio
                loop = asyncio.get_event_loop()
                loop.run_until_complete(main())
        """.format(
            user=self.bot.config['database']['user'],
            database=self.bot.config['database']['database'],
            port=self.bot.config['database']['port'],
            host=self.bot.config['database']['host'],
            data=', '.join(repr(i) for i in insert_statements),
        )
        file_content = textwrap.dedent(file_content).lstrip()

        # And donezo
        file = discord.File(io.StringIO(file_content), filename=f"_db_migrate_{guild_id or ctx.guild.id}.py")
        await ctx.send(file=file)

    @export.command(cls=utils.Command, name="table")
    @commands.bot_has_permissions(send_messages=True, attach_files=True)
    @utils.checks.is_config_set('database', 'enabled')
    @commands.is_owner()
    async def export_table(self, ctx:utils.Context, table_name:str):
        """
        Exports a given table from the database into a .csv file.
        """
        filename = f"./{table_name}_export.csv"

        # Make our initial file
        with open(filename, 'w') as f:
            f.write("")

        # Get the data we want to save
        async with self.bot.database() as db:
            await db.conn.copy_from_query('SELECT * FROM {table_name}'.format(table_name=table_name), output=filename, format='csv')
            column_descs = await db('DESCRIBE TABLE {table_name}'.format(table_name=table_name))

        # See what was written to the file
        with open(filename, 'r') as f:
            file_content = f.read()

        # Add our headers
        headers = ','.join([i['column_name'] for i in column_descs])

        # Write the new content to the file
        with open(filename, 'w') as f:
            f.write(headers + "\n" + file_content)

        # Send it to discord
        await ctx.send(file=discord.File(filename))

        # And delete the file
        if os.path.exists(filename):
            os.remove(filename)
        else:
            return


def setup(bot:utils.Bot):
    x = OwnerOnly(bot)
    bot.add_cog(x)
