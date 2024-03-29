"""Bot admin commands"""


import discord
from discord.ext import commands

import os

import constants
from file_storage import user_data, user_update_with_defaults
import utils


class Admin(commands.Cog, name='admin'):

    def __init__(self, client):
        self.client = client

    @commands.command(name='pid', aliases=['process'], description='get the process id of the bot.', usage='pid')
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def pid(self, ctx):
        if user_data[ctx.author.id]['is_admin']:
            await ctx.channel.send(f'This doens\'t really mean anything but:\n`PID:` **{os.getpid()}**')

    @commands.command(name='op', aliases=['operator'], description='bot admins', usage='op <user>')
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def op(self, ctx, user: discord.User):
        if user_data[ctx.author.id]['is_admin']:
            if user_data[user.id]['is_admin']:
                await ctx.channel.send('User is already bot admin.')
                return
            user_data[user.id]['is_admin'] = True
            if 'admin' not in user_data[user.id]['badge']:
                user_data[user.id]['badge'].append('admin')
            await ctx.channel.send(f'Successfully made **{user}** bot admin.')

    @commands.command(name='deop', description='deop bot admins', usage='deop <user>')
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def deop(self, ctx, user: discord.User):
        if user_data[ctx.author.id]['is_admin']:
            if not user_data[user.id]['is_admin']:
                await ctx.channel.send('User is not bot admin.')
                return
            user_data[ctx.author.id]['is_admin'] = False
            if 'admin' in user_data[user.id]['badge']:
                user_data[user.id]['badge'].remove('admin')
            await ctx.channel.send(f'Successfully deoped **{user}**.')

    @commands.command(name='botban', description='ban people from using this bot', usage='botban <user>')
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def botban(self, ctx, user: discord.User):
        if user_data[ctx.author.id]['is_admin']:
            if not user_data[user.id]['is_banned']:
                user_data[user.id]['is_banned'] = True
                await ctx.channel.send(f'Successfully bot banned **{user}**.')
            else:
                await ctx.channel.send('User was already bot banned.')

    @commands.command(name='botunban', description='unban people from botbanned.', usage='botunban <user>')
    async def botunban(self, ctx, user: discord.User):
        if user_data[ctx.author.id]['is_admin']:
            if user_data[user.id]['is_banned']:
                user_data[user.id]['is_banned'] = False
                await ctx.channel.send(f'Successfully pardoned **{user}**.')
            else:
                await ctx.channel.send('User is not bot banned.')

    @commands.command(name='addxp', description='add xp to a user', usage='addxp <user> <amount>')
    async def addxp(self, ctx, user: discord.User, amount: int):
        if user not in user_data:
            user_update_with_defaults(user.id)
        if user_data[ctx.author.id]['is_admin']:
            utils.add_xp(user.id, amount, cooldown=False)
            await ctx.channel.send(f'Successfully added **{amount}** xp to **{user}**.')

    @commands.command(name='addbadge', description='add a badge to a user', usage='addbadge <user> <badge>')
    async def addbadge(self, ctx, user: discord.User, badge: str):
        if user not in user_data:
            user_update_with_defaults(user.id)
        if user_data[ctx.author.id]['is_admin']:
            if badge not in constants.BADGES:
                await ctx.channel.send(f'Invalid badge. Valid badges are {utils.help_categories(constants.BADGES.keys())}')
                return

            if badge not in user_data[user.id]['badge']:
                user_data[user.id]['badge'].append(badge)
                await ctx.channel.send(f'Successfully added **{badge}** badge to **{user}**.')
            else:
                await ctx.channel.send('User already has that badge.')


async def setup(client):
    await client.add_cog(Admin(client))
