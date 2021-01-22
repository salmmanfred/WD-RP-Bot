import discord
import json


async def bounce_back(ctx):
    await ctx.send("bounce")


async def shop(ctx, server):
    embed_var = discord.Embed(title="SHOP", description='"A shop that will suit all your needs"', color=0x00ff00)
    shop_entries = server.get_shop_entries()
    if len(shop_entries) >= 10:
        return
    for x in shop_entries:
        embed_var.add_field(name=x.emoji + " " + x.name, value=x.value, inline=False)
    msg = await ctx.send(embed=embed_var)
    # emoji = '\N{REGIONAL INDICATOR E}'
    await msg.add_reaction("\:regional_indicator_a:")
