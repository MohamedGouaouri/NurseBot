import random
import string
import datetime
import requests
import json
import discord
import os
from discord.ext import commands
from discord.utils import get
from db import db_session, get_engine
from models import Poll, Task

token = os.environ.get("DISCORD_TOKEN")
client = commands.Bot(command_prefix="$")
client.remove_command('help')


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_raw_reaction_add(payload):
    session = db_session(get_engine())
    lastpoll = session.query(Poll).all()[-1]
    pollid = lastpoll.pollid
    channel = client.get_channel(payload.channel_id)
    if pollid == payload.message_id:
        message = await channel.fetch_message(payload.message_id)
        reaction = get(message.reactions, emoji=payload.emoji.name)
        print(reaction.count)


@client.command(aliases=["help"])
async def _help(ctx):
    embed = discord.Embed(title="Bot commands",
                          description="I\'m nurseBot :wink: how can I help you ?",
                          color=discord.Color.blue())
    embed.add_field(
        name="$random", value="Generate random number as we need them to make a decision", inline=False)
    embed.add_field(name="$poll", value="Create a poll.", inline=False)
    embed.add_field(name="$add", value="Add a new task", inline=False)
    embed.add_field(name="$tasks", value="List your tasks", inline=False)
    embed.add_field(name="$advice", value="Get an advice", inline=False)
    embed.add_field(
        name="$clear", value="Clear < amount > of messages.", inline=False)
    embed.add_field(name="$joke", value="Get a funny joke", inline=False)
    await ctx.send(embed=embed)


@client.command()
async def clear(ctx, amount=1):
    print(type(ctx.author))
    await ctx.channel.purge(limit=int(amount))


@client.command(aliases=["random"])
async def random_number(ctx, *, param):
    try:
        start = param.split(" ")[0]
        end = param.split(" ")[1]
        r = random.randint(int(start), int(end))
        await ctx.send(f"random number: {r}")

    except Exception as e:
        print(e)


@client.command()
async def poll(ctx, *, options):
    embed = discord.Embed(title="New poll is here",
                          description="I\'m nurseBot :wink: We are doing a poll here",
                          color=discord.Color.blue())

    used_emojis = ["🇦", "🇧", "🇨", "🇩"]
    list_of_options = options.split(",")
    value = ""
    for i, o in enumerate(list_of_options):
        l = string.ascii_lowercase[i]
        value += f":regional_indicator_{l}: {o} \n\n"
    embed.add_field(name="Poll",
                    value=value,
                    inline=False)
    poll = await ctx.send(embed=embed)
    for i in range(len(list_of_options)):
        await poll.add_reaction(used_emojis[i])

    # save poll into db
    db_engine = get_engine()
    session = db_session(db_engine)
    session.add(Poll(pollid=poll.id))
    session.commit()


@client.command(aliases=["add"])
async def task_add(ctx, *, task):
    db_engine = get_engine()
    session = db_session(db_engine)
    session.add(Task(task_name=task))
    session.commit()

    await ctx.channel.send(f"{ctx.message.author} added a new task **{task}**")


@client.command()
async def tasks(ctx):
    embed = discord.Embed(title="Your tasks",
                          description="I\'m nurseBot :wink: Those are your tasks",
                          color=discord.Color.blue())

    db_engine = get_engine()
    session = db_session(db_engine)
    tasks = session.query(Task).all()
    for task in tasks:
        embed.add_field(name=f"Task {task.task_id}",
                        value=f"{task.taskname}", inline=False)
    await ctx.send(embed=embed)


@client.command()
async def advice(ctx):
    r = requests.get("https://api.adviceslip.com/advice")
    advice = json.loads(r.content)['slip']['advice']
    await ctx.send("_"+advice+"_")


@client.command()
async def joke(ctx):
    r = requests.get(
        "https://official-joke-api.appspot.com/jokes/programming/random")
    setup = r.json()[0]['setup']
    punchline = r.json()[0]['punchline']
    await ctx.send(f"{setup}: \n _{punchline}_")


@client.command()
async def angry(ctx):
    embed = discord.Embed(title=f"{ctx.message.author} is angry",
                          description="",
                          color=discord.Color.blue())
    embed.set_image(
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR8vOc-DcI2NWuTRmQ-dekgQoXs8QG_tb3vTQ&usqp=CAU")


@client.command()
async def happy(ctx):
    embed = discord.Embed(title=f"{ctx.message.author} is happy",
                          description="",
                          color=discord.Color.blue())
    embed.set_image("data:image/jpeg;base64,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")


@client.command()
async def sad(ctx):
    embed = discord.Embed(title=f"{ctx.message.author} is sad",
                          description="",
                          color=discord.Color.blue())
    embed.set_image(
        "https://cdn.myanimelist.net/s/common/uploaded_files/1469214306-7154b29733fc2483b7f04dbfb48ccd1a.jpeg")
client.run(token)
