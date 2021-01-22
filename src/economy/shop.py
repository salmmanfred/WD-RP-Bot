import discord

async def bounce_back(ctx):
    await ctx.send("bounce")

async def shop(ctx):
    embedVar = discord.Embed(title="Title", description="Desc", color=0x00ff00)
    for x in range(10):
        embedVar.add_field(name="Field"+str(x), value="hi", inline=False)
    ctx.channel.send(embedVar)