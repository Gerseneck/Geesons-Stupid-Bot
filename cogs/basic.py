"""Basic bot commands"""

import discord
from discord.ext import commands

import math
import random
import time

import constants
import utils
import file_storage


class Basic(commands.Cog, name='basic'):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Stuff to respond with when a command raises an error."""

        error_type = error.__class__
        if isinstance(error_type, commands.BadArgument):
            if error_type in {commands.MemberNotFound, commands.GuildNotFound}:
                await ctx.send('Error: bad user or member argument. Try mentioning them or using the ID.')
            elif error_type == commands.ChannelNotFound:
                await ctx.send('Error: bad channel argument. Try #tagging it or using the ID.')
            elif error_type == commands.ChannelNotReadable:
                await ctx.send('Error: bad channel argument. I cannot access that channel, please give me permissions.')
            elif error_type == commands.RoleNotFound:
                await ctx.send(
                    'Error: bad role argument. Try using the ID (right click in the role list on your profile).')
            else:
                await ctx.send('Error: bad argument [unknown type].')
        elif error_type == commands.NoPrivateMessage:
            await ctx.send('Sorry, this command does not function in a private message.')
        elif error_type == commands.CommandOnCooldown:
            if error.retry_after > 60:
                minutes = math.floor(error.retry_after / 60)
                sec = f'{error.retry_after - (minutes * 60):.1f}'
                return await ctx.send(embed=discord.Embed(color=constants.random_color(),
                                                          description=f'This command is currently on cooldown, Try again after **{minutes}m {sec}s**.'))
            await ctx.send(embed=discord.Embed(color=constants.random_color(),
                                               description=f'This command is currently on cooldown, Try again after {error.retry_after:.1f}s.'))
        elif error_type == commands.MissingPermissions:
            await ctx.send(
                f'You do not have the permissions necessary to execute this command. Needed: {error.missing_perms}')
        elif error_type == commands.BotMissingPermissions:
            await ctx.send(
                f'I do not have the permissions necessary to execute this command. Needed: {error.missing_perms}')
        elif error_type == commands.MissingRequiredArgument:
            await ctx.send(
                f'```\n[Error] Missing Argument: {error}\n\n----- Usage is below -----\n{ctx.command.usage}\n\n\n[] = optional field```')
        elif error_type == commands.BadLiteralArgument:
            await ctx.send(
                f'```\n[Error] Bad Literal Argument: Invalid value for "{str(error.param).split(":")[0]}"\n\nValid Values: {error.literals}\n\n----- Usage is below -----\n{ctx.command.usage}\n\n\n[] = optional field```')
        else:
            raise RuntimeError(f'Uncaught exception: {error_type.__name__}: {error_type}') from error

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.client.user:
            return
        if message.author.bot:
            return
        if message.channel.type == discord.ChannelType.private:
            return

        file_storage.guild_update_with_defaults(message.guild.id)
        file_storage.user_update_with_defaults(message.author.id)

        if file_storage.user_data[message.author.id]['is_banned'] \
                and message.content.startswith(file_storage.guild_data[message.guild.id]['prefix']):
            return

        if file_storage.user_data[message.author.id]['xp_cooldown'] + 15 <= time.time():
            utils.add_xp(message.author.id, random.randint(1, 5))

    @commands.command(name='help', aliases=['commands', 'command', 'cmd', 'cmds', 'ls'],
                      description='Help command, shows all commands.', usage='help [*sub_command]')
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def help(self, ctx, sub_command: str = ''):
        if file_storage.user_data[ctx.author.id]['is_banned']:
            return
        client_commands = {}
        for command in self.client.commands:
            client_commands[command.name] = [command.description, command.aliases, command.usage]
        client_cogs = {'basic': 'basic commands',
                       'configuration': 'configurations',
                       'economy': 'economy commands',
                       'fun': 'fun commands that are really not that fun',
                       'games': 'just some casual games you can play.', 'image': 'images using pillow',
                       'moderation': 'moderation to make your server better',
                       'admin': 'commands only for bot admins', }

        if not sub_command:

            title = 'Commands'
            description = f'for more information do `help <category>`\n[invite link]({constants.INVITE_LINK})'
            name = 'Categories'
            val = utils.help_categories(list(client_cogs))

        elif sub_command.lower() in client_cogs:

            cog = self.client.get_cog(sub_command.lower())
            cmd = [x.name for x in cog.get_commands()]

            title = f'{sub_command.lower()[0].upper()}{sub_command.lower()[1:]}'
            description = f'for more information do `help <command-name>`'
            name = 'Commands'
            val = utils.help_categories(cmd)

        elif sub_command.lower() in client_commands:

            command_description = client_commands[sub_command][0]
            command_aliases = client_commands[sub_command][1]
            command_usage = client_commands[sub_command][2]

            title = sub_command
            description = command_description
            name = ''
            val = f'Aliases: {utils.help_categories(command_aliases)}\nUsage: `{command_usage}`\n[] = optional field'

        else:
            await ctx.send('That is not a valid command or category.')
            return

        embed = discord.Embed(title=title,
                              description=description,
                              color=constants.random_color())
        embed.add_field(name=name, value=val, inline=False)
        await ctx.send(embed=embed)

    @commands.command(name='hello', description='hello', usage='hello')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def hello(self, ctx):
        if file_storage.user_data[ctx.author.id]['is_banned']:
            return
        await ctx.send(f'Hello, {ctx.author.name}.')

    @commands.command(name='say', description='make the bot say stuff', usage='say <msg>')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def say(self, ctx, *, msg):
        if file_storage.user_data[ctx.author.id]['is_banned']:
            return
        await ctx.send(msg)

    @commands.command(name='latency', description='latency of the bot', usage='latency', aliases=['ping'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def latency(self, ctx):
        if file_storage.user_data[ctx.author.id]['is_banned']:
            return
        await ctx.send(f'This number really doesn\'t matter: `{round(self.client.latency * 1000, 1)}` ms.')

    @commands.command(name='xp', description='shows user\'s xp', usage='xp [user]', aliases=['level', 'lvl'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def xp(self, ctx, user: discord.Member = None):
        if file_storage.user_data[ctx.author.id]['is_banned']:
            return
        user = ctx.author if user is None else user
        if user not in file_storage.user_data:
            file_storage.user_update_with_defaults(user.id)

        level = file_storage.user_data[user.id]['level']
        xp = file_storage.user_data[user.id]['xp']
        next_level = file_storage.user_data[user.id]['next_level']
        percent = round(xp / next_level * 100, 2)

        embed = discord.Embed(color=constants.random_color())
        embed.set_author(name=f'{user.name}\'s XP', icon_url=user.avatar.url if user.avatar else user.default_avatar.url)
        embed.add_field(name='', value=f'**Level**: {level:,}\n**XP**: {xp:,}/{next_level:,} ({percent}%)')
        await ctx.send(embed=embed)


async def setup(client):
    await client.add_cog(Basic(client))
