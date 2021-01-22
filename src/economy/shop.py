import discord
import json
async def bounce_back(ctx):
    await ctx.send("bounce")

async def shop(ctx):
    embedVar = discord.Embed(title="SHOP", description='"A shop that will suit all your needs"', color=0x00ff00)
    shopjson = json.load(open("economy/shop.json","r"))
    if len(shopjson) >= 10:
        return 
    for x in shopjson:
        embedVar.add_field(name=x["emoji"]+" "+x["name"], value=x["val"], inline=False)
    msg = await ctx.send(embed=embedVar)
    #emoji = '\N{REGIONAL INDICATOR E}'
    await msg.add_reaction("\:regional_indicator_a:")