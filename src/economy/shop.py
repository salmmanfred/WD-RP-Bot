import discord
from discord.ext.commands import Context

messages = []


def cache_message(msg):
    global messages
    if len(messages) >= 49:
        messages = []
    messages.append(msg.id)


async def clear_cache(ctx):
    global messages
    embed_var = discord.Embed(title="CACHE", description='CACHE', color=0x00ff00)
    s = "C"
    for x in messages:
        s = s + str(x) + "\n"
    embed_var.add_field(name="cache", value=s, inline=False)
    messages = []
    await ctx.reply(embed=embed_var)


async def cache(ctx):
    global messages
    embed_var = discord.Embed(title="CACHE", description='CACHE', color=0x00ff00)
    s = "Cache:\n"
    for x in messages:
        s = s + str(x) + "\n"
    embed_var.add_field(name="cache", value=s, inline=False)
    await ctx.reply(embed=embed_var)


async def bounce_back(ctx):
    await ctx.send("bounce")


async def shop(ctx: Context, server, types):
    embed_var = discord.Embed(title="SHOP", description='"A shop that will suit all your needs"', color=0x00ff00)
    shop_entries = server.get_shop_entries(page=types)
    # server.add_shop_entry("Ammunition",100,"🇦", page="ammo")
    if len(shop_entries) >= 10:
        return
    emojis = []
    for i in shop_entries:
        embed_var.add_field(name=i.item.name, value=f" {i.emoji} : {i.value}", inline=False)
        emojis.append(i.emoji)
    msg = await ctx.reply(embed=embed_var)
    for i in shop_entries:
        await msg.add_reaction(i.emoji)
    cache_message(msg)


async def shop_short(ctx):
    embed_var = discord.Embed(title="SHOP", description='"A shop that will suit all your needs"', color=0x00ff00)
    embed_var.add_field(name="Gun shop", value="wd!shop gun", inline=True)
    embed_var.add_field(name="Ammunition shop", value="wd!shop ammo", inline=True)
    await ctx.reply(embed=embed_var)


async def buy(reaction, user, server, bot):
    embeds = None
    page = reaction.message.reference.resolved.content.replace("wd!shop", "").strip()
    print(page)
    shopen = server.get_shop_entries(page=page)
    if reaction.message.id in messages:
        if user.id == reaction.message.reference.resolved.author.id:
            for x in shopen:
                if str(reaction) == str(x.emoji):
                    try:
                        server.remove_funds(user.id, x.value)
                        server.give(user.id, x.item)
                        embeds = discord.Embed(title="Confirmation", description="Purchase confirmation")
                        embeds.add_field(name=x.item.name, value=str(x.value), inline=False)
                        embeds.add_field(name="Remaning funds", value=server.get_account(user.id).balance)
                    except ValueError:
                        embeds = discord.Embed(title="Failed", description="You don't have the funds to make that transfer")

            await user.send(embed=embeds)

    if reaction.message.author.id == bot.user.id:
        if user.id != bot.user.id:
            await reaction.message.remove_reaction(reaction, user)
