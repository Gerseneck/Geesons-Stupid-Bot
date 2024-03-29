"""Configuration commands"""


import discord
from discord.ext import commands

import math

import constants
import file_storage


class Configuration(commands.Cog, name='configuration'):

    def __init__(self, client):
        self.client = client

    @commands.command(name='serverinfo', aliases=['guildinfo', 'guild', 'server'],
                      description='check server information', usage='serverinfo')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def serverinfo(self, ctx):

        features = 'None' if not ctx.guild.features else '\n'.join(ctx.guild.features)
        channel_amount = len(ctx.guild.text_channels)
        vc_amount = len(ctx.guild.voice_channels)
        creation_date = math.floor(ctx.guild.created_at.timestamp())
        embed = discord.Embed(title='Server Info', color=constants.random_color())
        embed.set_author(name=f'{ctx.guild}', icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
        embed.add_field(name='Basic',
                        value=f'**Member Count:** {ctx.guild.member_count}\n**Creation Date:** <t:{creation_date}> (<t:{creation_date}:R>)\n**Owner:** {ctx.guild.owner.metion}\n**Text Channels:** {channel_amount}\n**Voice Channels:** {vc_amount}\n**Boosts:** {ctx.guild.premium_subscription_count}')
        embed.add_field(name='Security',
                        value=f'**2fa:** {ctx.guild.mfa_level.name}\n**Verification Level:** {ctx.guild.verification_level}')
        embed.add_field(name='Features', value=f'{features}', inline=False)
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        await ctx.channel.send(embed=embed)

    @commands.command(name='userinfo', aliases=['user'], description='check user information', usage='userinfo <user>')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def userinfo(self, ctx, user: discord.User = None):

        user = ctx.author if user is None else user

        creation_date = math.floor(user.created_at.timestamp())

        embed = discord.Embed(title='User Info', color=constants.random_color())
        embed.set_author(name=user, icon_url=user.avatar.url if user.avatar else user.default_avatar.url)
        embed.add_field(name='General Information', value=f'**ID**: {user.id}\n**Creation Date:** <t:{creation_date}> (<t:{creation_date}:R>)')
        embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
        await ctx.channel.send(embed=embed)


async def setup(client):
    await client.add_cog(Configuration(client))
