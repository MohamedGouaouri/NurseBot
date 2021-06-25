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


@client.command(aliases=["tasks"])
async def _tasks(ctx):
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


@client.command(aliases=["5bich"])
async def _5bich(ctx):
    jokes = [
             "MCSI li maderch MCT bien ghi makan lah y3awel",
             "L Allia 9alet le MCT est la partie la plus défficle fi MERISE :panik:",
             "L Allia 9alet kayna une solution unique fi MCT :panik:",
             "bon 5bich",
             ]
    await ctx.send(random.choice(jokes))


@client.command()
async def angry(ctx):
    file = discord.File("reactions/angry.png")
    await ctx.send(f"{ctx.message.author.name} is angry", file=file)


@client.command()
async def happy(ctx):

    file = discord.File("reactions/smile.png")
    await ctx.send(f"{ctx.message.author.name} is happy", file=file)


@client.command()
async def sad(ctx):
    file = discord.File("reactions/cry.png")
    await ctx.send(f"{ctx.message.author.name} is sad", file=file)


def days_hours_minutes(td):
    return td.days, td.seconds//3600, (td.seconds//60) % 60


@client.command()
async def countdown(ctx):
    # coutndown to our exam
    with open("exams.json", "r") as f:
        calendar = json.load(f)
    found = False
    i = 0
    while not found:
        exam_date = datetime.datetime(
            2021, 6, calendar[i]['date'], calendar[i]['hour'], calendar[i]['minute'])
        current_date = datetime.datetime.utcnow()
        left = exam_date - current_date
        (days, hours, minutes) = days_hours_minutes(left)
        if days < 0 or hours < 0 or minutes < 0:
            i += 1
        else:
            found = True
    if not found:
        await ctx.send(f"Yaaay exams are over")
        return
    exam_of = calendar[i]['name']
    if days == 0 and hours != 0 and minutes != 0:
        await ctx.send(f"{hours} hours and {minutes} minutes left for {exam_of} exam ... good luck")
        return

    if days == 0 and hours == 0 and minutes != 0:
        await ctx.send(f"{minutes} for {exam_of} exam ... left")
        return

    await ctx.send(f"{days} days, {hours} hours {minutes} minutes left fo for {exam_of} exam ... good luck")


client.run(token)
