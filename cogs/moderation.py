"""Moderation Commands"""
import typing

import discord
from discord.ext import commands

import asyncio
import string

from file_storage import guild_data


class Moderation(commands.Cog, name='moderation'):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.channel.id in guild_data[message.guild.id]['antidelete']:
            user = message.author
            for i in guild_data[message.guild.id]['log']['antidelete']:
                embed = discord.Embed(title='Message Deleted', color=discord.Color.red())
                embed.set_author(name=user.name,
                                 icon_url=user.avatar.url if user.avatar else user.default_avatar.url)
                embed.add_field(name='Message', value=message.content, inline=False)
                embed.add_field(name='Channel', value=message.channel.mention, inline=False)
                await self.client.get_channel(i).send(embed=embed)

    @commands.command(name='prefix', description='change the prefix for the server', usage='prefix [prefix]')
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.has_permissions(manage_guild=True)
    async def prefix(self, ctx, *, msg: str = ''):
        if not msg or msg.lower() == 'bot':
            guild_data[ctx.guild.id]['prefix'] = 'bot '
            await ctx.channel.send(f'Reset the prefix to `bot`.')
            return
        if msg[-1] not in string.punctuation and msg[-1] not in string.digits:
            msg += ' '
        if len(msg) > 10:
            await ctx.send('You may not have a prefix longer than 10 characters.')
            return
        guild_data[ctx.guild.id]['prefix'] = msg
        await ctx.channel.send(
            f'Successfully set the prefix to `{msg}`.\n\nIf your prefix ends with a symbol or number, you do not have '
            f'the add a space between the prefix and the command.')

    @commands.command(name='kick', description='kick users', usage='kick <user> [reason]')
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.Member, *, reason: str = ''):
        if user == self.client.user:
            await ctx.channel.send("You can't kick me with my own command you know.")
            return
        if user == ctx.guild.owner:
            await ctx.channel.send('That\'s the owner you dumbo.')
            return
        if user == ctx.author:
            await ctx.channel.send('Do you want me to kick you or no?')
            return
        await ctx.guild.kick(user, reason=reason)
        await ctx.channel.send(f'Successfully kicked **{user}**.')
        await user.send(f'You got kicked from **{ctx.guild.name}** by: {ctx.author}, reason: {reason}')

    @commands.command(name='ban', description='ban users', usage='ban <user> [reason]')
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.User, *, reason=''):
        if user == self.client.user:
            await ctx.channel.send("You can't ban me with my own command you know.")
            return
        if user == ctx.guild.owner:
            await ctx.channel.send('That\'s the owner you dumbo.')
            return
        if user == ctx.author:
            await ctx.channel.send('Do you want me to ban you or no?')
            return
        await ctx.guild.ban(user, reason=reason)
        await ctx.channel.send(f'Successfully banned **{user}**.')
        await user.send(f'You got banned from **{ctx.guild.name}** by: {ctx.author}, reason: {reason}')

    @commands.command(name='purge', aliases=['delete'], description='delete multipul messages at once',
                      usage='purge [amount]')
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def purge(self, ctx, amount: int = 2):
        if amount <= 1:
            return await ctx.channel.send('You must at least delete 2 messages.')
        await ctx.channel.purge(limit=amount + 1)
        purged_msg = await ctx.channel.send(f'Successfully purged **{amount}** messages.')
        await asyncio.sleep(1)
        await purged_msg.delete()

    @commands.command(name='antidelete', description='make users unable to delete messages', usage='antidelete [channel]')
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def antidelete(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel
        if channel.id not in guild_data[ctx.guild.id]['antidelete']:
            guild_data[ctx.guild.id]['antidelete'].append(channel.id)
            await ctx.channel.send(f'Turned on antidelete for {channel.mention}.')
            if not guild_data[ctx.guild.id]['log']['antidelete']:
                await ctx.channel.send('**WARNING: You currently do not have a log channel set up for antidelete yet.**\nRun `log <channel> antidelete` to set one up.')
        else:
            guild_data[ctx.guild.id]['antidelete'].remove(channel.id)
            await ctx.channel.send(f'Turned off antidelete for  {channel.mention}.')

    @commands.command(name='slowmode', aliases=['sm'], description='set custom slowmodes', usage='slowmode <time>')
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def slowmode(self, ctx, slowmode: int = 0):
        if slowmode < 0:
            await ctx.channel.send("Your slowmode can't be a negative number")
        if slowmode > 21600:
            await ctx.channel.send(f'Your int ({slowmode}) cannot be larger than **21600**.')
        await self.client.get_channel(ctx.channel.id).edit(reason='custom slowmode', slowmode_delay=int(slowmode))
        await ctx.channel.send(f'Set slowmode of <#{ctx.channel.id}> to **{slowmode}** seconds.')

    @commands.command(name='lock', description='lock the channel', usage='lock [channel]')
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def lock(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        if not channel.permissions_for(ctx.guild.default_role).send_messages:
            await ctx.channel.send(f'<#{ctx.channel.id}> is already locked.')
            return
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.channel.send(f'Locked <#{ctx.channel.id}>.')

    @commands.command(name='unlock', description='unlock a channel', usage='unlock [channel]')
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def unlock(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        if channel.permissions_for(ctx.guild.default_role).send_messages:
            await ctx.channel.send(f'<#{ctx.channel.id}> is not locked.')
            return
        await channel.set_permissions(ctx.guild.default_role, send_messages=True)
        await ctx.channel.send(f'Unlocked <#{ctx.channel.id}>.')
        
    @commands.command(name='log', description='set up a channel for logging', usage='log <channel> [purpose]')
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def log(self, ctx, channel: discord.TextChannel, *, purpose: typing.Literal['antidelete'] = 'antidelete'):
        if channel.id not in guild_data[ctx.guild.id]['log'][purpose]:
            guild_data[ctx.guild.id]['log'][purpose].append(channel.id)
            await ctx.channel.send(f'Successfully setup {channel.mention} for logging.')
        else:
            guild_data[ctx.guild.id]['log'][purpose].remove(channel.id)
            await ctx.channel.send(f'Successfully removed {channel.mention} from logging.')


async def setup(client):
    await client.add_cog(Moderation(client))
