import discord
from discord.ext.commands import Context
import json


async def bounce_back(ctx):
    await ctx.send("bounce")


async def shop(ctx: Context, server):
    embed_var = discord.Embed(title="SHOP", description='"A shop that will suit all your needs"', color=0x00ff00)
    shop_entries = server.get_shop_entries()
    if len(shop_entries) >= 10:
        return
    emojis = []
    for x in shop_entries:
        embed_var.add_field(name=f"{x.name}", value=f"{x.emoji}: {x.value}", inline=False)
        emojis.append(x.emoji)
    msg = await ctx.send(embed=embed_var)
    # emoji = '\N{REGIONAL INDICATOR E}'
    for i in emojis:
        await msg.add_reaction(i)

